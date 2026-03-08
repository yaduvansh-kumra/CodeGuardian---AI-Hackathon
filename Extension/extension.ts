import * as vscode from 'vscode';
import axios from 'axios';

// This function runs the exact moment your extension is activated
export function activate(context: vscode.ExtensionContext) {
    
    // We register the command we defined in package.json
    let disposable = vscode.commands.registerCommand('codeguardian.evaluateCode', async () => {
        
        // 1. Get the active text editor and the code the student highlighted
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage("Please open a file and select some code first!");
            return;
        }

        const selection = editor.selection;
        const selectedCode = editor.document.getText(selection);

        if (!selectedCode) {
            vscode.window.showErrorMessage("Please highlight the AI-generated code you want to evaluate.");
            return;
        }

        // 2. Setup our 3-strike loop variables
        let attempts = 0;
        const maxAttempts = 3;
        let passed = false;
        let previousHints = "";

        // 3. Start the evaluation loop
        while (attempts < maxAttempts && !passed) {
            attempts++;

            // Pop up an input box at the top of the screen asking for the explanation
            const explanation = await vscode.window.showInputBox({
                prompt: `Attempt ${attempts}/3: Explain this code to unlock it. ${previousHints}`,
                placeHolder: "E.g., This function takes two parameters and returns their sum...",
                ignoreFocusOut: true // Prevents the box from closing if they click away
            });

            // If the student hits Escape to cancel the box, stop everything
            if (explanation === undefined) {
                vscode.window.showInformationMessage("Evaluation cancelled.");
                return;
            }

            // 4. Send the data to your AWS API and show a loading spinner
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "CodeGuardian: Grading your explanation...",
                cancellable: false
            }, async (progress) => {
                
                try {
                    // This is your actual AWS API Gateway URL!
                    const response = await axios.post('https://qne8z9rsye.execute-api.ap-south-1.amazonaws.com/grade', {
                        code: selectedCode,
                        explanation: explanation,
                        language: "python", // Hardcoded for MVP, but can be dynamic later
                        eli5: false
                    });

                    const result = response.data;

                    // 5. Evaluate the score
                    if (result.score >= 70) {
                        passed = true;
                        vscode.window.showInformationMessage(`🎉 Success! Score: ${result.score}. ${result.overallcomment}`);
                    } else {
                        // They failed this attempt. Save the hint for the next loop.
                        previousHints = `Hint: Focus on ${result.issues[0] || "understanding the logic better."}`;
                        vscode.window.showWarningMessage(`Score: ${result.score}. Not quite right. Try again!`);
                    }

                } catch (error) {
                    vscode.window.showErrorMessage("Server error while grading. Please try again.");
                    console.error(error);
                    // Break the loop if the server crashes so we don't trap the user
                    passed = true; 
                }
            });
        }

        // 6. The ELI5 Fallback (If they failed 3 times)
        if (!passed) {
            vscode.window.showErrorMessage("3 strikes! Activating ELI5 teaching mode...");
            
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "CodeGuardian: Generating ELI5 lesson...",
            }, async () => {
                try {
                    // Call the API again, but this time with eli5: true
                    const eli5Response = await axios.post('https://qne8z9rsye.execute-api.ap-south-1.amazonaws.com/grade', {
                        code: selectedCode,
                        explanation: "Failed 3 times",
                        language: "python",
                        eli5: true
                    });

                    const lesson = eli5Response.data;
                    
                    // Show the simple explanation and the verification question in a big modal popup
                    vscode.window.showInformationMessage(
                        `🧑‍🏫 ELI5 Lesson: ${lesson.eli5_explanation}\n\nQuestion: ${lesson.verify_question}`, 
                        { modal: true }
                    );

                } catch (error) {
                    vscode.window.showErrorMessage("Failed to load ELI5 mode.");
                }
            });
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}