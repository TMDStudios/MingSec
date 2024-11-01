document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'green';
    setTheme(savedTheme);

    if(window.location.pathname === '/') handleHomePage();
});

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    // Workaround for input stying issue
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        const parent = input.parentNode;
        const nextSibling = input.nextSibling;

        parent.removeChild(input);

        const newInput = input.cloneNode(true);
        parent.insertBefore(newInput, nextSibling);
    });
}

function handleHomePage(){
    document.getElementById('themes').innerHTML += '<p><a href="/logout">Exit</a></p>';

    document.addEventListener('DOMContentLoaded', function(){
        const form = document.getElementById('camRequestForm');

        form.addEventListener('submit', function(event){
            event.preventDefault();
            const formData = new FormData(form);
            fetch(form.action,{
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => {
                if(response.ok){
                    form.reset();
                    return response.json();
                }else{
                    throw new Error('Unable to send request. The length value must be between 1 and 60.');
                }
            })
            .then(data => {
                alert(data.message);
            })
            .catch(error => {
                alert('Error: ' + error.message);
            });
        });
    });

    fetchLogFiles();
}

function fetchLogFiles(){
    fetch('/fetch-log-files/')
        .then(response => response.json())
        .then(data => {
            const logFileLinksDiv = document.getElementById('log-file-links');
            logFileLinksDiv.innerHTML = '';

            data.log_files.forEach(file => {
                const p = document.createElement('p');
                const a = document.createElement('a');
                a.href = '#';
                a.className = 'log-link';
                a.dataset.logFile = file;
                a.textContent = file;
                p.appendChild(a);
                logFileLinksDiv.appendChild(p);
            });

            attachLogLinkListeners();

            if(data.log_files.length > 0){
                fetchLogData(data.log_files[0]);
            }
        })
        .catch(error => {
            console.error('Error fetching log files:', error);
        });
}

function attachLogLinkListeners() {
    document.querySelectorAll('.log-link').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const logFile = this.dataset.logFile;
            fetchLogData(logFile);
        });
    });
}

function fetchLogData(logFile) {
    const logContentDiv = document.getElementById('log-content');
    const loadingMessageDiv = document.getElementById('loading-message');

    loadingMessageDiv.style.display = 'block';
    logContentDiv.innerHTML = '';

    fetch(`/fetch-log/?log_file=${encodeURIComponent(logFile)}`)
        .then(response => response.json())
        .then(data => {
            loadingMessageDiv.style.display = 'none';

            data.log_data.forEach(line => {
                const p = document.createElement('p');
                p.textContent = line;
                p.classList.add('log-line');
                logContentDiv.appendChild(p);
            });
        })
        .catch(error => {
            console.error('Error fetching log:', error);
            loadingMessageDiv.style.display = 'none';
        });
}