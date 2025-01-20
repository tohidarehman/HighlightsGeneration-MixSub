const generatedHighlight = document.getElementById('GeneratedHighlight');
const highlightGenerationForm = document.getElementById('HighlightGenerationForm');
const generateHighlightButton = document.getElementById('GenerateHighlightButton');
const preferredModel = document.getElementById('PreferredModel');

if (!(highlightGenerationForm instanceof HTMLFormElement)) {
    throw new Error('highlightGenerationForm is not an instance of HTMLFormElement');
}

if (!(generatedHighlight instanceof HTMLParagraphElement)) {
    throw new Error('generatedHighlight is not an instance of HTMLParagraphElement');
}

if (!(generateHighlightButton instanceof HTMLInputElement)) {
    throw new Error('generateHighlightButton is not an instance of HTMLInputElement');
}

if (!(preferredModel instanceof HTMLSelectElement)) {
    throw new Error('preferredModel is not an instance of HTMLSelectElement');
}

highlightGenerationForm.addEventListener('submit', async function (event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    event.stopPropagation();

    const selectedModel = preferredModel.options[preferredModel.selectedIndex];
    const modelTask = selectedModel.dataset.task;

    generateHighlightButton.disabled = true;
    generatedHighlight.innerText = 'Generating Highlight...';

    const data = new FormData(highlightGenerationForm);

    const payload = {
        paper_content: data.get('PaperContent')?.toString(),
        preferred_model: data.get('PreferredModel')?.toString(),
        maximum_tokens: parseInt(data.get('MaximumTokens')?.toString() || '1', 10),
        model_task: modelTask,
    };

    try {
        const resp = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        const data = await resp.json();

        if (!resp.ok) {
            console.log(data);
            generatedHighlight.innerText = data['detail'];
        } else {
            generatedHighlight.innerText = data['output'];
        }
    } catch (e) {
        if (e instanceof Error) {
            generatedHighlight.innerText = e.message;
        } else {
            generatedHighlight.innerText = 'Error: ' + e;
        }
    } finally {
        generateHighlightButton.disabled = false;
    }
});
