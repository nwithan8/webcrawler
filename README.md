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
