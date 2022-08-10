job "lbp-print-api" {
  datacenters = ["dc1"]

  group "lbp-print-api-group" {
    count = 1

    volume "lbp-print-api-cache" {
      type      = "host"
      read_only = true
      source    = "lbp-print-api-cache"
    }

    network {
      port  "lbp-print-api-starticport"{
        to = 5000
      }
      port "workerport" {}
      port "redisport" {}
    }

    service {
      name = "lbp-print-api"
      port = "lbp-print-api-starticport"

      tags = [
        "traefik.enable=true",
        "traefik.http.routers.lbpprintapi-https.tls=true",
        "traefik.http.routers.lbpprintapi-https.rule=Host(`print.lombardpress.com`)",
        "traefik.http.routers.lbpprintapi-https.tls.certresolver=myresolver",
        "traefik.http.routers.lbpprintapi-https.tls.domains[0].main=print.lombardpress.com",
        "traefik.http.routers.lbpprintapi-http.rule=Host(`print.lombardpress.com`)",
        "traefik.http.routers.lbpprintapi-http.middlewares=https_only",
        

     ]

      check {
        type     = "http"
        path     = "/"
        interval = "2s"
        timeout  = "2s"
      }
    }

    task "app" {
      driver = "podman"

      config {
        image = "jeffreycwitt/lbp-print-api"
        volumes = [
          "/home/jcwitt/lbp-print-cache:/usr/src/app/cache:Z"
        ]
        ports = ["lbp-print-api-starticport"]
        command = "gunicorn -w 1 -b 0.0.0.0:5000 app:app"
      }
    }
    task "queue-worker" {
      driver = "podman"

      config {
        image = "jeffreycwitt/lbp-print-api"
        volumes = [
          "/home/jcwitt/lbp-print-cache:/usr/src/app/cache:Z"
        ]
        ports = ["workerport"]
        command = "python3 worker.py"
      }
      env{
        REDIS_ENDPOINT= "redis"
      }
    }
    task "redis" {
      driver = "podman"
      config {
        image = "redis:alpine"
        ports = ["redisport"]
      }
      env{
        REDIS_ENDPOINT= "redis"
      }
    }
  }
}%