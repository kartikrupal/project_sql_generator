document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const generateBtn = document.getElementById('generateBtn');
    const naturalLanguageInput = document.getElementById('naturalLanguageInput');
    const sqlOutput = document.getElementById('sqlOutput');
    const loader = document.getElementById('loader');
    const copyBtn = document.getElementById('copyBtn');
    const messageBox = document.getElementById('messageBox');

    // --- Event Listeners ---
    generateBtn.addEventListener('click', handleGenerateSql);
    copyBtn.addEventListener('click', copyToClipboard);

    /**
     * Main function to handle the SQL generation process.
     */
    async function handleGenerateSql() {
        const userInput = naturalLanguageInput.value.trim();

        if (!userInput) {
            showMessage('Please enter a description first.', 'error');
            return;
        }

        toggleLoading(true);
        sqlOutput.textContent = '';
        copyBtn.classList.add('hidden');
        messageBox.textContent = '';

        try {
            const sqlCode = await generateSqlWithBackend(userInput);
            
            if (sqlCode) {
                sqlOutput.textContent = sqlCode;
                copyBtn.classList.remove('hidden');
            } else {
                 showMessage('The AI could not generate SQL. Please try rephrasing.', 'error');
            }

        } catch (error) {
            console.error('Error generating SQL:', error);
            showMessage('An error occurred. Please check the console.', 'error');
        } finally {
            toggleLoading(false);
        }
    }

    /**
     * Calls our backend API to generate SQL from a text prompt.
     */
    async function generateSqlWithBackend(prompt) {
        const response = await fetch('/generate-sql', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `API request failed with status ${response.status}`);
        }

        const result = await response.json();
        
        if (result.sql_code) {
            return result.sql_code;
        } else {
            console.warn("Unexpected API response structure:", result);
            return null;
        }
    }

    /**
     * Toggles the visibility of the loading indicator.
     */
    function toggleLoading(isLoading) {
        loader.classList.toggle('hidden', !isLoading);
        generateBtn.disabled = isLoading;
        if(isLoading) {
            generateBtn.classList.add('opacity-70', 'cursor-not-allowed');
        } else {
            generateBtn.classList.remove('opacity-70', 'cursor-not-allowed');
        }
    }

    /**
     * Copies the generated SQL code to the clipboard.
     */
    function copyToClipboard() {
        const textToCopy = sqlOutput.textContent;
        if (!textToCopy) return;

        if (navigator.clipboard) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                showMessage('Copied to clipboard!', 'success');
            }).catch(err => {
                console.error('Could not copy text: ', err);
                fallbackCopyTextToClipboard(textToCopy);
            });
        } else {
            fallbackCopyTextToClipboard(textToCopy);
        }
    }

    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.top = "0";
        textArea.style.left = "0";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            showMessage('Copied to clipboard!', 'success');
        } catch (err) {
            console.error('Fallback: Oops, unable to copy', err);
            showMessage('Failed to copy.', 'error');
        }
        document.body.removeChild(textArea);
    }

    /**
     * Displays a message to the user.
     */
    function showMessage(text, type) {
        messageBox.textContent = text;
        messageBox.className = `mt-4 text-center h-5 ${type === 'success' ? 'text-green-400' : 'text-red-400'}`;
        setTimeout(() => {
            if (messageBox.textContent === text) {
               messageBox.textContent = '';
            }
        }, 3000);
    }
});