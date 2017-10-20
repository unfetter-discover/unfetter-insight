# UNFETTER-INSIGHT

![Babelfish logo](http://mjmobbs.com/wp-content/uploads/2010/08/babel.jpg)

**Unfetter Insight** performs natural language processing and analysis to detect possible ATT&CK Patterns.

### Starting

In order to make it work you need [Docker](https://docs.docker.com).

Once you've your docker environment ready, clone this repo.

```sh
$ git clone https://github.com/unfetter-discover/unfetter-insight.git
$ cd unfetter-insight/
$ docker build . -t babelfish:latest
$ docker run -p 8080:8080 babelfish
```

Now your unfetter-insight instance is ready and running at `http://localhost:8080`

Usage(Babelfish Package)
-----------------------------------
To use babelfish package for report classification, simply do:
	
	>>>import babelfish
	>>>babelfish.classify_report('sample.txt')
	100%|████████████████████████████████████████| 278/278 [00:00<00:00, 663.89it/s]
	['Bypass User Account Control']
	

	