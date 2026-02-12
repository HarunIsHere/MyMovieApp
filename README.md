<style type="text/css">.rendered-markdown{font-size:14px} .rendered-markdown>*:first-child{margin-top:0!important} .rendered-markdown>*:last-child{margin-bottom:0!important} .rendered-markdown a{text-decoration:underline;color:#b75246} .rendered-markdown a:hover{color:#f36050} .rendered-markdown h1, .rendered-markdown h2, .rendered-markdown h3, .rendered-markdown h4, .rendered-markdown h5, .rendered-markdown h6{margin:24px 0 10px;padding:0;font-weight:bold;-webkit-font-smoothing:antialiased;cursor:text;position:relative} .rendered-markdown h1 tt, .rendered-markdown h1 code, .rendered-markdown h2 tt, .rendered-markdown h2 code, .rendered-markdown h3 tt, .rendered-markdown h3 code, .rendered-markdown h4 tt, .rendered-markdown h4 code, .rendered-markdown h5 tt, .rendered-markdown h5 code, .rendered-markdown h6 tt, .rendered-markdown h6 code{font-size:inherit} .rendered-markdown h1{font-size:28px;color:#000} .rendered-markdown h2{font-size:22px;border-bottom:1px solid #ccc;color:#000} .rendered-markdown h3{font-size:18px} .rendered-markdown h4{font-size:16px} .rendered-markdown h5{font-size:14px} .rendered-markdown h6{color:#777;font-size:14px} .rendered-markdown p, .rendered-markdown blockquote, .rendered-markdown ul, .rendered-markdown ol, .rendered-markdown dl, .rendered-markdown table, .rendered-markdown pre{margin:15px 0} .rendered-markdown hr{border:0 none;color:#ccc;height:4px;padding:0} .rendered-markdown>h2:first-child, .rendered-markdown>h1:first-child, .rendered-markdown>h1:first-child+h2, .rendered-markdown>h3:first-child, .rendered-markdown>h4:first-child, .rendered-markdown>h5:first-child, .rendered-markdown>h6:first-child{margin-top:0;padding-top:0} .rendered-markdown a:first-child h1, .rendered-markdown a:first-child h2, .rendered-markdown a:first-child h3, .rendered-markdown a:first-child h4, .rendered-markdown a:first-child h5, .rendered-markdown a:first-child h6{margin-top:0;padding-top:0} .rendered-markdown h1+p, .rendered-markdown h2+p, .rendered-markdown h3+p, .rendered-markdown h4+p, .rendered-markdown h5+p, .rendered-markdown h6+p{margin-top:0} .rendered-markdown ul, .rendered-markdown ol{padding-left:30px} .rendered-markdown ul li>:first-child, .rendered-markdown ul li ul:first-of-type, .rendered-markdown ol li>:first-child, .rendered-markdown ol li ul:first-of-type{margin-top:0} .rendered-markdown ul ul, .rendered-markdown ul ol, .rendered-markdown ol ol, .rendered-markdown ol ul{margin-bottom:0} .rendered-markdown dl{padding:0} .rendered-markdown dl dt{font-size:14px;font-weight:bold;font-style:italic;padding:0;margin:15px 0 5px} .rendered-markdown dl dt:first-child{padding:0} .rendered-markdown dl dt>:first-child{margin-top:0} .rendered-markdown dl dt>:last-child{margin-bottom:0} .rendered-markdown dl dd{margin:0 0 15px;padding:0 15px} .rendered-markdown dl dd>:first-child{margin-top:0} .rendered-markdown dl dd>:last-child{margin-bottom:0} .rendered-markdown blockquote{border-left:4px solid #DDD;padding:0 15px;color:#777} .rendered-markdown blockquote>:first-child{margin-top:0} .rendered-markdown blockquote>:last-child{margin-bottom:0} .rendered-markdown table th{font-weight:bold} .rendered-markdown table th, .rendered-markdown table td{border:1px solid #ccc;padding:6px 13px} .rendered-markdown table tr{border-top:1px solid #ccc;background-color:#fff} .rendered-markdown table tr:nth-child(2n){background-color:#f8f8f8} .rendered-markdown img{max-width:100%;-moz-box-sizing:border-box;box-sizing:border-box} .rendered-markdown code, .rendered-markdown tt{margin:0 2px;padding:0 5px;border:1px solid #eaeaea;background-color:#f8f8f8;border-radius:3px} .rendered-markdown code{white-space:nowrap} .rendered-markdown pre>code{margin:0;padding:0;white-space:pre;border:0;background:transparent} .rendered-markdown .highlight pre, .rendered-markdown pre{background-color:#f8f8f8;border:1px solid #ccc;font-size:13px;line-height:19px;overflow:auto;padding:6px 10px;border-radius:3px} .rendered-markdown pre code, .rendered-markdown pre tt{margin:0;padding:0;background-color:transparent;border:0}</style>
<div class="rendered-markdown"><h1>Movie App 🎥 (SQL + OMDb API)</h1>
<p>A simple movie library application that lets you manage a movie collection from the command line, store it in SQLite (via SQLAlchemy), and fetch movie data from the OMDb API.</p>
<h2>Features</h2>
<ul>
<li><strong>SQL Storage (SQLite + SQLAlchemy)</strong></li>
<li><strong>Add movie via OMDb API</strong> (enter title only)</li>
<li><strong>CRUD</strong></li>
<li>List movies</li>
<li>Add movie (API)</li>
<li>Delete movie</li>
<li>Update rating (kept for compatibility)</li>
<li><strong>Analytics</strong></li>
<li>Stats (average/median/best/worst)</li>
<li>Random movie</li>
<li>Search / suggestions</li>
<li>Sort by rating / year</li>
<li>Filter by rating and year range</li>
</ul>
<h2>Project Structure</h2>
<p>Movie_SQL_HTML_API/
<br  />├─ movies.py
<br  />├─ storage/
<br  />│  ├─ init.py
<br  />│  └─ movie_storage_sql.py
<br  />├─ data/
<br  />│  └─ movies.db                (ignored by git)
<br  />├─ _static/
<br  />│  ├─ index_template.html
<br  />│  └─ style.css
<br  />├─ requirements.txt
<br  />├─ .gitignore
<br  />└─ README.md</p>
<h2>Setup</h2>
<h3>1) Create and activate a virtual environment (recommended)</h3>
<pre><code class="bash">python3 -m venv .venv
source .venv/bin/activate
</code></pre>
<h3>2) Install dependencies</h3>
<pre><code class="bash">pip install -r requirements.txt
</code></pre>
<h2>OMDb API Key</h2>
<p>This project uses the OMDb API to fetch movie data.</p>
<p>In <code>movies.py</code>, set:</p>
<pre><code class="python">OMDB_API_KEY = "YOUR_KEY_HERE"
</code></pre>
<h2>Run the app</h2>
<pre><code class="bash">python3 movies.py
</code></pre>
<h2>Notes</h2>
<ul>
<li><code>data/movies.db</code> is runtime data and is not committed to git (see <code>.gitignore</code>).</li>
</ul>
</div>