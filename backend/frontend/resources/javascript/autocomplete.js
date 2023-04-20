
const toggle_display = () => {
    main = document.getElementById("main-content");
    loading = document.getElementById("loading-screen");

    console.log(main.classList);

    if (main.classList[0] == "visible") {
        main.classList = ["hidden"]
        loading.classList = ["visible position-absolute top-50 start-50 translate-middle w-25 h-25"];
    } else {
        main.classList = ["visible"];
        loading.classList = ["hidden"];
    }

    console.log(main);
}

const fetchPapers = async () => {
    let response = await fetch(
        `https://api.openalex.org/autocomplete/works?q=${search_term}`
    ).then(res => res.json());

    return response.results;
};

const getId = (papers) => {
    let paper = papers.find(p => p.display_name === search_term)
    let work_id = paper.id.split('/').pop();

    return work_id;
}

const showPapers = async () => {
    const ul = document.createElement('ul');
    ul.classList.add('papers');
    results.innerHTML='';

    let papers = [];
    papers = await fetchPapers();

    papers.forEach(paper => {
        const li = document.createElement('li');
        li.classList.add('paper-item');

        const p = document.createElement('p')
        p.innerHTML = paper.display_name;

        li.appendChild(p)
        li.addEventListener('click', e => {
            search_term = li.childNodes[0].textContent;
            search_input.value = search_term;
            selected_paper_id = getId(papers);
            results.innerHTML = '';
        });

        ul.appendChild(li);
    });

    results.appendChild(ul);
};

search_input.addEventListener('input', async e => {
    search_term = e.target.value;
    await showPapers();
});