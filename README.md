Burdock
=========

Burdock is a cheap Python knock-off of [Dandelion](https://github.com/scttnlsn/dandelion).

How is it different from Dandelion?
--------------------

  - Only supports FTP
  - Supports named profiles
  - dry-run mode
  - ... and fake deployments
  - Doesn't let you specify additional files to upload. This is because I only just noticed that feature in Dandelion
  - It might not work worth a damn

Why?
---

I don't know Ruby much beyond editing my Compass config file.
Burdock is intended to do one specific thing: deploy git repository contents to FTP servers. If you're stuck using FTP for deployment in 2013, things are bad enough to warrant the existence of such a program. It deliberately doesn't include support for anything more, since there are much better ways of deploying code than by FTP.

Config
---

Burdock is almost completely compatible with Dandelion. In fact, I'm so lazy that it uses dandelion.yml as its default config file.

    profiles:
        foo:
            username: foo@foo.com
            password: barbar
            host: myhost.com
        bar:
            host: myhost.com
            path: /somewhere/else
    scheme: ftp
    host: example.com
    username: jsmith 
    password: itsasecret
    path: /public_html/my_site
    exclude:
    - .gitignore

Here, `scheme` is optional and ignored because Burdock only does FTP.
I see no use case for anything else. If I've got shell access to a host, I'm going to deploy it properly anyway.

Use case
---

Jane has a site she inherited and she wishes she had better revision control. There's only FTP access to the client's server and using Dandelion to deploy would initially upload all the files in the repository at 3.8Kb/s on her PitifulNet connection. So instead, she runs

    burdock deploy --fake
and it pops a file on to the server saying it's up to date with the current HEAD. Quick and easy. Next week she uploads some changes to a staging server:

    burdock deploy --profile staging
    
which effectively takes any settings under the `staging` profile in preference to the defaults.

When she's happy that works, she runs

    burdock deploy --profile production --dryrun
    
and it goes through the motions, letting her see what files will be overwritten on the live `production` site before

    burdock deploy --profile production
    
knocks it out.

Version
-

0.1

Installation
--------------

Yeah, I haven't written a setup script yet.
There's a requirements file you can use with pip:

    pip install -r requirements.txt

You might have to do that with `sudo`, depends how your machine is set up.
and then you can symlink it or alias it to `burdock` or something. Knock yourself out.

FAQ
---

  Q: Is it robust?
  A: Does the Pope shit in the woods? No. It's early days and I haven't even really tested it yet.
  Q: Will it work on Windows?
  A: I don't care. And neither should you.

    
License
-

[WTFPL](http://wtfpl.net)
