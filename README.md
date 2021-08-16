# webcrawler
This is a personal coding challenge for me to document my growth in programming.

After attending Google I/O 2018, I decided to take on the world with my own web crawler. This was one of my first Python projects.

A year later, I decided to start over from scratch (not even looking at the old 2018 code) and rewrite the program. A year of programming learning later, and my code was far cleaner, smaller and more efficient.

I hope to commit myself to revisiting this project every year.

Previous versions of the project are available by changing the branch.

# Overview:
### **2018**:

* **Lines**: *638 (including large blocks of commented-out code)*
* **Structure**: Starts at hard-coded URL, first scanning for same-domain pages, storing in an array (function uses regex to find and check domain for a match). Stores other-domain pages in a separate array. First visits same-domain pages, then other-domain pages, storing an array of found links in a twin array (tracked by indexOf location). Webpage content is scraped with BeautifulSoup and stored alongside page URL in a database. Arrays are also printed in an external file.

**I would advise against trying to run this code. This script is bloated and abandoned, and possibly incomplete.**


### **2019**:

* **Lines**: *103*
* **Structure**: Starts at URL passed in through CLI arguments (also option to restrict scraping to just the starting domain). Rather than arrays, using a dictionary to store {URL: [links found on this page], [pages that link to this page]}. Strips # (anchors) and ? from URL to avoid unnecessarily scraping and storing the same webpage multiple times. Also ignores specific image, video, audio and PDF URL endings to avoid attempting to scrape non-webpages. Scraping runs recursively. Dictionary is written to a file. No web content is stored; just mapping the references between webpages.


### **2020**:

* **Lines**: *148*
* **Structure**: No major CLI changes compared to 2019 version, except using proper argument parsing with argparse. Introducing classes! Actual object-oriented programming! Each webpage is an object, with array attributes that store what page the current page came from, and what pages the current page goes to. Admittedly, URL list is not stored in permanent storage (like a text file, for now). Better checking for ignored file extensions. Better string formatting. Scraping still done recursively. Array stores previously-visited links, each link checked and ignored if in the array.

### **2021**:

* **Lines**: *I didn't count*
* Let's introduce the biggest change: a proper database. So long to the JSON array saved in a text file. We're utilizing SQLAlchemy to store Pages in an SQLite3 database, along with the Relationship (parent-child) between two pages.
* This structure change encourages a better division of classes across files, and a better folder structure for helper classes. There's a lot of helper utilities (imported from other projects I've worked on).
* For ease, we've removed the ability to save pages, since it added a lot of overhead.
* An earlier version of this iteration was working just fine, but its method of recursion caused branching. For example, say we go to Site X, which has 20 links to other pages on it. We take the first link, which takes us to Site Y. Site Y has 10 links to other pages on it. We take the first link, which takes us to Site Z. Yes, we're collecting all the links from the sites, but right now, we're on Site Z, when we haven't visited the other 19 links from Site X yet. After the database was properly working, we replaced the recursion (we often hit the recursion limit), replacing it with a LinkAndParentList tracker, employing a FIFO approach. Any new links discovered are added to the end of the growing list of links, while those at the beginning of the list are addressed first. This ensures that we'll visit and collect links from all the links on Site X, before we start going to all the links on Site Y, before we go to all the links on Site Z. We had a similar approach in the version from previous years, but it was initially lost during the redesign for database work. This is, however, better than previous implementations, since we are actively popping the first item in the list, rather than having to keep track of the current index.
* We've also revamped the functions that decide whether to bother with a site. For example, we do a HEAD request to a site to see if it returns a 404. A 404 site may still have a webpage with links on it, but we found it often results in an endless loop of 404 links. This does seem to depend on the site itself though, and whether they return 404 for bad requests, or try to resolve the page endlessly. 
  * For example, Cloudflare will return a 404 for this repeating page: https://support.cloudflare.com/hc/en-us/articles/200170016-What-is-Email-Address-Obfuscation-/hc/change_language/de/hc/change_language/de/hc/change_language/de/hc/change_language/de/hc/change_language/de/hc/change_language/de/hc/change_language/de/hc/change_language/de/hc/change_language/de/hc/change_language/de.
  * But Facebook doesn't return a 404 for this repeating page, causing an infinite loop (at least, until you hit the 1400 URL character limit): https://www.facebook.com/business/partner-directory/search/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business/business?solution_type=campaign_management
* We've also added a proper requirements.txt file!
* We're still running into issues of hitting non-webpages (i.e., photos, ZIP files, EXE files) that stall or even error out the download process. In the future, we'll need to improve the HEAD request to see what we're dealing with.
* Handling SSL is also on the list of 2022 improvements
