const search_input = document.getElementById('search');
const results = document.getElementById('results');
const depth_input = document.getElementById('depth');
const tooltipElement = document.getElementById('tooltip');
//const visualization_div = document.getElementById('visualization');

let search_term = '';
let selected_paper_id = '';
let papers;

// Open Alex has a rate limit of 10 per second, setting this to 2 shows now errors on my machine,
// but at 3 I start getting limited.
const CONCURRENCY_LIMIT = 2;