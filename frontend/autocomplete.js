const search_input = document.getElementById('search');
const results = document.getElementById('results');

let search_term = '';
let papers;

const fetchPapers = async () => {
    papers = await fetch(
        `https://api.openalex.org/autocomplete/works?q=${search_term}`
    ).then(res => res.json());
};


const showPapers = async() => {
    results.innerHTML = '';

    await fetchPapers(search_term);

    console.log(papers)

    const ul = document.createElement('ul');
    ul.classList.add('papers');

    papers.results.forEach(paper => {
        const li = document.createElement('li');
        li.classList.add('paper-item');

        const p = document.createElement('p')
        p.innerHTML = paper.display_name;

        li.appendChild(p)
        li.addEventListener('click', e => {
            search_term = li.childNodes[0].textContent;
            search_input.value = search_term;
            results.innerHTML = '';
        });

        ul.appendChild(li);
    });

    results.appendChild(ul);
};

showPapers();

search_input.addEventListener('input', e => {
    search_term = e.target.value;
    showPapers();
});