// Only use for home page
if(window.location.pathname === '/'){
    document.querySelectorAll('.log-link').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const logFile = this.dataset.logFile;
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
        });
    });
}