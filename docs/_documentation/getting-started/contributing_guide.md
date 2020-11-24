---
layout: default
title: Contributing Guide
nav_order: 2
permalink: /getting-started/contributing_guide/
parent: Getting Started
---
# Contributing Guide

Thank you for considering contributing to `dame-flame`. Contributions are welcome from first time or advanced users, as are stories of use cases. 

Any learning algorithm can be used to predict covariate importance, beyond the ones we have chosen to incorporate, based on our impression of the most valuable algorithms. These can easily be added, using standard off-the-shelf methods, as a new feature. 

There are many other ways to contribute to the package. We welcome contributers who wish to report any unexpected bugs, clean or maintain code, add details or use cases to the documentation, and add more test cases.

## Submitting Bug Reports or Feature Requests

Please open an issue on Github here: [https://github.com/almost-matching-exactly/DAME-FlAME-Python-Package/issues/](https://github.com/almost-matching-exactly/DAME-FlAME-Python-Package/issues/)

If this is a bug request, we ask that you describe the issue in as much detail as possible, including a description of expected results and experienced results. An example including datasets if possible could also be helpful. This is because reproducing an issue is critical to fixing it. 

If this is a feature request, we ask that you describe your use case and link any relevant references, in order for us to ensure that our features will meet your needs. You can also email our team to discuss if that is easier for you. 

## Contributing Code

Please contribute to the code using standard open source protocol. In brief, after forking the repository on github, edit your files locally (We prefer to use the Sypder IDE for this), commit changes to your fork, and submit a pull request with a detailed explanation of your contributions.

Below are some tips that will ensure your pull request is approved smoothly, with minimal requests for changes:

 - Make sure your code passes the tests to ensure algorithm correctness in the /tests/ folder. Do this by running the following command from your terminal in the package repository:
{% highlight markdown %}
pytest
{% endhighlight %}

- Ensure that your code meets our style guide standards for readability. We mostly adhere to the Google Python Style Gude, found [here](https://google.github.io/styleguide/pyguide.html). 

- Ensure that your code meets our maintainability standards. We aim to ensure highly modularized, short code that is easy to use, debug, and maintain. If you can refactor anything, do it. 

- Write a test for your code, write an example illustrating it, and update the documentation accordingly. The documentation is found in the 'docs' folder of the Github here: [https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package](https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package). We recommend using Visual Studio Code. The documentation can be compiled and previewed using the command:
{% highlight markdown %}
bundle exec jekyll serve
{% endhighlight %}

## Questions

If you have any questions or need assistance with a contribution, please reach out to our team. Contact neha.r.gupta "at" duke "dot" edu. 
