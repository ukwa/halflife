The Hundred Thousands
=====================

This repository has been created to hold the results of experiments on a random sample of the holdings of the [Open UK Web Archive](http://www.webarchive.org.uk/).  

Link Half-Life
--------------

The goal is to randomly sample URLs from previous years of the web archive, and for each one determine its current status. Has is long since gone? Or is it still online? With a few thousand URLs, it should be possible to build up a reasonably accurate picture of the 'half-life' of the URLs in our archive.

Step 1. Random Sampling
-----------------------

All of our content is indexing in Apache Solr, so we can use that to generate random samples of content for each crawl year. The largest sample contains one hundred thousand archived URLs, hence the name of this repository.

The first step is to randomly sample N links from each year from Solr. Faceting by year looks something like:

<http://localhost:8080/discovery/select?q=*%3A*&wt=json&indent=true&rows=0&facet.range.gap=%2B1YEAR&facet.range=crawl_date&f.crawl_date.facet.range.start=1980-01-01T00:00:00Z&f.crawl_date.facet.range.end=2020-01-01T00:00:00Z&facet=on>

Then something link this to sample randomly:

<http://chrome.bl.uk:8080/solr/select/?q=*:*&rows=1&sort=random_2%20desc&fq=timestamp:[2004-01-01T00:00:00Z%20TO%202005-01-01T00:00:00Z]>

In fact, the easiest way is simply to generate lots of random sample outputs and store the JSON offline, then process that.

I wrote a script to do this, called `yearwise-sampler.py`.

So, I randomly sampled 100 URLs from each year of the Solr index of the Selective Archive, and stored the files a sub-folder (`./halflife`).

I can then run a suitable status checked against that sample.
    

Step 2. Checking Current Status Of The Samples
----------------------------------------------

Then, periodically, for each sample, we revisit those links and attempt to determine what has happened to them.

DETAILS

* **OK** - Host and URL known: got a 200 response at the original URL
* **MOVED** - Host and URL known: got a 200 response after following any 3xx redirects.
* **MISSING** - Host is known, but URL returned a 404 or similar, after zero or more 3xx redirects.
* **ERROR** - Host is known, but URL returned a 500 or similar, after zero or more 3xx redirects.
* **GONE** - No connection possible (UNRESOLVABLE, UNREACHABLE, CONNECTION-REFUSED etc.).

This works reasonably well, although it does not compare the contents, so the **OK** and **MOVED** really only refers to the URL itself. If we add the ability to determine similarity of the content, then we have:

* **UNCHANGED** - Host and URL known: got an identical 200 response at the original URL
* **MOVED** - Host and URL known: got an identical 200 response after following any 3xx redirects.
* **CHANGED** - Host and URL known: got an different 200 response at the original URL
* **REDIRECTED** - Host and URL known: got an different 200 response after following any 3xx redirects.
* **MISSING** - Host is known, but URL returned a 404 or similar, after zero or more 3xx redirects.
* **ERROR** - Host is known, but URL returned a 500 or similar, after zero or more 3xx redirects.
* **GONE** - No connection possible (UNRESOLVABLE, UNREACHABLE, CONNECTION-REFUSED etc.).

Although **CHANGED** and **REDIRECTED** could probably be merged really.

Those results are also added to this repository.

DETAILS


Step 3. Publish The Overall Status
----------------------------------

The results from the hundred thousand are then turned into an appropriate graph, and made available 

DETAILS