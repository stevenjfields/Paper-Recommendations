
const toggle_display = () => {
    main = document.getElementById("main-content");
    loading = document.getElementById("loading-screen");

    if (main.classList[0] == "visible") {
        main.classList = ["hidden"]
        loading.classList = ["visible position-absolute top-50 start-50 translate-middle w-25 h-25"];
    } else {
        main.classList = ["visible"];
        loading.classList = ["hidden"];
    }
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
    results.innerHTML='';

    let papers = [];
    papers = await fetchPapers();

    // take last 10 as a hacky fix for more than 10 items being in
    // the papers list
    papers.slice(-10).forEach(paper => {
        const item = document.createElement('div');
        item.innerHTML = paper.display_name;

        item.addEventListener('click', e => {
            search_term = paper.display_name;
            search_input.value = search_term;
            selected_paper_id = getId(papers);
            results.innerHTML = '';
        });

        results.append(item)
    });
};

search_input.addEventListener('input', async e => {
    search_term = e.target.value;
    await showPapers();
});