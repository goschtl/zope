
backend plone {
    .host = "localhost";
    .port = "10081";
}

director balancer round-robin {
    {
        .backend = plone;
    }
}

sub vcl_recv {

    set req.backend = balancer;

    if (req.request != "GET" && req.request != "HEAD") {
        if (req.request == "PURGE") {
            if (!client.ip ~ purge) {
                    error 405 "Not allowed.";
            }
            lookup;
        }
        pipe;
    }
    if (req.http.Expect) {
        pipe;
    }

    /* Always cache images */
    if (req.url ~ "\.(jpg|jpeg|gif|png|tiff|tif|svg|swf|ico|css|js|vsd|doc|ppt|pps|xls|pdf|mp3|mp4|m4a|ogg|mov|avi|wmv|sxw|zip|gz|bz2|tgz|tar|rar|odc|odb|odf|odg|odi|odp|ods|odt|sxc|sxd|sxi|sxw|dmg|torrent|deb|msi|iso|rpm|kss)$") {
        lookup;
    }
    /* Always cache CSS and javascript */
    if (req.url ~ "\.(css|js)$") {
        lookup;
    }

    /* Do not cache other authorised content */
    if (req.http.Authenticate || req.http.Authorization) {
        pass;
    }

    /* We only care about the "__ac.*" cookies, used for authentication */
    if (req.http.Cookie && req.http.Cookie ~ "__ac(_(name|password|persistent))?=") {
        pass;
    }

    if (req.http.Cookie && req.http.Cookie ~ "_ZopeId") {
        pass;
    }


    lookup;
}

sub vcl_hit {
    if (req.request == "PURGE") {
            set obj.ttl = 0s;
            error 200 "Purged";
    }
}
sub vcl_miss {
    if (req.request == "PURGE") {
            error 404 "Not in cache";
    }
}
 
sub vcl_fetch {
    if (!obj.cacheable) {
        pass;
    }
    if (obj.http.Set-Cookie) {
        pass;
    }
    set obj.ttl = 1800s;
}

sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }
    set resp.http.Server = "Unknown";
}  

