# Setting up Redirects to Other Domains We Own

The main domains owned by UKMON are `ukmeteors.co.uk` which hosts the Archive, and `ukmeteornetwork.org` which hosts the public facing website.

In addition we own several similar-named domains, `ukmeteornetwork.com`, `ukmeteornetwork.uk`, `ukmeteornetork.org,uk` and `ukmeteornetwork.net`. These are all registered with AWS for convenience and cost reasons.

## Redirects

Each domain is set up to redirect to `ukmeteornetwork.org`. This is done as follows

- `lighttpd` is set up on the batch server, with a single index page that redirects to `ukmeteornetwork.org`
- Hosted Zones are set up in Route53 for each domain. The configuration for this is managed in [terraform](../archive/terraform/route53.tf)
- In each Zone, A records for each domain apex and the www variant, again managed via Terraform.

## Lighttpd and LetsEncrypt

`lighttpd` is installed with default settings, however to configure SSL i followed [these instructions](https://redmine.lighttpd.net/projects/lighttpd/wiki/HowToSimpleSSL). Use the HTTP-01 / certbot section.

To summarise the process:

- set up `lighttpd` with temporary self-signed certs and restart it.
- install `certbot` and run it to create externally-signed SSL certs.
- create softlinks in `/etc/lighttpd/certs/www.ukmeteornetwork.com` to the Letsencrypt certs in `/etc/letsencrypt/live/www.ukmeteornetwork.com/`.
- update `lighttpd` configuration to use the new certs.
- restart `lighttpd`.

Certbot requires access to the webserver on ports 80 and 443. This is done in the Terraform module that creates  [ec2SecurityGroup](../archive/terraform/secgrp.tf)

## lighttpd index page

``` html
<head>
        <title>Redirecting...</title>
      <META http-equiv="refresh" content="5;URL=http://www.ukmeteornetwork.org">
<body>
        <h2>
        Our website address is <a href="https://ukmeteornetwork.org">https://ukmeteornetwork.org</a>, please update your bookmarks!
        <br>
        Redirecting you shortly ...
</body>
</head>

```
