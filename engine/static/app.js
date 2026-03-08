document.addEventListener("DOMContentLoaded", () => {
    const promptField = document.getElementById("prompt");
    const generateBtn = document.getElementById("generateBtn");
    const clearBtn = document.getElementById("clearBtn");

    if(promptField){
            promptField.addEventListener("keydown", (e) => {
                if(e.key === "Enter" && !e.shiftKey && !e.repeat){
                    e.preventDefault();
                    generate();
                }
            })
        }

    if(generateBtn){ 
        generateBtn.addEventListener("click", generate);
    }

    if(promptField && clearBtn){
        const toggleVisibility = () => {
            clearBtn.style.opacity = promptField.value.trim() ? "1" : "0";
        }
        promptField.addEventListener("input", toggleVisibility);

        clearBtn.addEventListener("click", () => {
            promptField.value = "";
            promptField.focus();
            toggleVisibility();
        })
        toggleVisibility();
    }
    loadHistory();
})


async function generate() {
    const promptField = document.getElementById("prompt");
    const loader = document.getElementById("loader");
    const codeElement = document.getElementById("output");
    const generateBtn = document.getElementById("generateBtn");

    const prompt = promptField?.value || "";
    if(!prompt.trim()){ alert("Prompt required"); return; }

    tokenCount = 0;
    codeElement.textContent = "";

    loader.style.display = "block";
    generateBtn.disabled = true;
    
    startTimer(loader);

    let fullText = "";

    try{
        const response = await fetch("/api/code/generate/", {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt })
        });

        if(!response.ok){
            codeElement.textContent = "Server error";
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while(true){
            const {done, value} = await reader.read();
            if(done) break;

            const chunk = decoder.decode(value);

            fullText += chunk;

            tokenCount += chunk.split(/\s+/).length;
        }   

        const parsed = extractCodeBlock(fullText)

        applyLanguage(parsed.lang);

        codeElement.textContent = parsed.code;

        Prism.highlightElement(codeElement);

        promptField.value = "";
        loadHistory();
    }catch(err){
        if(codeElement) codeElement.textContent = "Connection error";
    }finally{
        stopTimer(loader);
        if(generateBtn) generateBtn.disabled = false;
    }
}


async function loadHistory() {
    const container = document.getElementById("history");
    if(!container) return;
    
    const response = await fetch("/api/code/history/");
    const data =  await response.json();

    container.innerHTML = "";

    data.forEach(entry => {
        const div = document.createElement("div");
        div.className = "history-item";

        const text = document.createElement("span");
        text.className = "history-text";
        text.textContent = entry.prompt.substring(0, 40);

        const delBtn = document.createElement("button");
        delBtn.className = "history-delete";
        delBtn.innerHTML = `
        <svg viewBox="0 0 24 24" width="14" height="14">
            <path d="M6 6 L18 18 M18 6 L6 18"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"/>
        </svg>
        `;

        delBtn.onclick = async () => {
            await deleteEntry(entry.id);
            loadHistory();
        };

        div.appendChild(text);
        div.appendChild(delBtn);

        div.onclick = (e) => {
            if(e.target === delBtn) return;
            const promptField = document.getElementById("prompt");
            const outputField = document.getElementById("output");

            if(promptField)promptField.value = entry.prompt;
            if(outputField){
                outputField.textContent = entry.response;
                Prism.highlightElement(outputField);
            }
        }
        container.appendChild(div);
    })
}



async function deleteEntry(id) {
    try{
        const response = await fetch(`/api/code/history/${id}/`, {
            method: "DELETE"
        });
        if(!response.ok){
            console.error("Delete failed");
            alert("Delete failed");
        }    
    }catch(err){
        console.error("Connection error")
    }
}



let timerInterval = null;
let tokenCount = 0;

function startTimer(loader){
    const startTime = Date.now();

    timerInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;
        loader.textContent = `Generating.. ${elapsed.toFixed(1)}s | tokens: ${tokenCount}`;
    }, 100);
}

function stopTimer(loader){
    if(timerInterval){
        clearInterval(timerInterval);
        timerInterval = null;
    }
    loader.style.display = "none";
}


function extractCodeBlock(text){
    const match = text.match(/```(\w+)?\n([\s\S]*?)```/);
    
    if(!match) return { lang: "plaintext", code: text};

    return { lang: match[1] || "plaintext", code: match[2]}
}

function applyLanguage(lang){
    const code = document.getElementById("output-code");
    code.className = "";
    code.classList.add("language-" + lang);
}