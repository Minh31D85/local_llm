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
            input.value = "";
            promptField.focus();
            toggleVisibility();
        })
        toggleVisibility();
    }

    loadHistory();
})


async function generate() {
    const promptField = document.getElementById("prompt");
    const prompt = promptField?.value || "";
    const loader = document.getElementById("loader");
    const output = document.getElementById("output");
    const generateBtn = document.getElementById("generateBtn");

    if(!prompt.trim()){
        alert("Prompt required");
        return;
    }

    if(loader) loader.style.display = "block";
    if(output) output.textContent = "";
    if(generateBtn)generateBtn.disabled = true;

    try{
        const response = await fetch("/api/code/generate/", {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt })
        });

        const data = await response.text();

        if(!response.ok){
            output.textContent = data.error || "Server error";
            return;
        }

        output.textContent = data.response;

        if(promptField) promptField.value = "";
        
        loadHistory();
    }catch(err){
        if(output) output.textContent = "Connection error";
    }finally{
        if(loader) loader.style.display = "none"; 
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
            if(outputField)outputField.textContent = entry.response;
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