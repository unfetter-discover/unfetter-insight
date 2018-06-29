# UNFETTER-INSIGHT

![Babelfish logo](http://mjmobbs.com/wp-content/uploads/2010/08/babel.jpg)

**Unfetter Insight** performs natural language processing and analysis to detect possible ATT&CK Patterns.

### Starting

In order to make it work you need [Docker](https://docs.docker.com).

Once you've your docker environment ready, download the tar file from the disc, un-tar the files, go into the unfetter-insight directory, and compose the flask.

```sh
$ git clone https://github.com/unfetter-discover/unfetter-insight.git
$ cd unfetter-insight/
$ docker-compose up
```

Now your unfetter-insight instance is ready and running at `http://localhost:8080`

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

	