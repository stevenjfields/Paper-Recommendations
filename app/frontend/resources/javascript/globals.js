const search_input = document.getElementById('search');
const results = document.getElementById('results');
const depthInput = document.getElementById('depth');
const tooltipElement = document.getElementById('tooltip');
const progressBar = document.getElementById('progress-bar');
const progress_status = document.getElementById("status");
const progressDetails = document.getElementById("details");
const colorScheme = document.getElementById("color-scheme");

let search_term = '';
let selected_paper_id = 'W2963403868';


// Open Alex has a rate limit of 10 per second, setting this to 2 shows no errors on my machine,
// but at 3 I start getting limited.
const CONCURRENCY_LIMIT = 1;
const DEBUG = true;