# UNFETTER-INSIGHT

![Babelfish logo](http://mjmobbs.com/wp-content/uploads/2010/08/babel.jpg)

**Unfetter Insight** Performs natural language processing and analysis to detect possible ATT&CK Patterns.  Unfetter insight currently accepts files with the following extensions: .txt, .pdf, and .html .

### Starting

In order to run babelfish you will need [Docker](https://docs.docker.com).

Once you have finished setting up your docker environment, clone the unfetter-insight project from GitHub, and proceed to build the docker images:


```sh
$ git clone https://github.com/unfetter-discover/unfetter-insight.git
$ cd unfetter-insight/
$ docker-compose up
```

Now your unfetter-insight instance is up and running at `http://localhost:8080`

Usage(Babelfish Package)
-----------------------------------
To use babelfish package for report classification, simply do:

```sh
$ python
	>>>import babelfish
	>>>babelfish.classify_report('sample.txt')
	100%|████████████████████████████████████████| 278/278 [00:00<00:00, 663.89it/s]
	['Bypass User Account Control']
```	

	