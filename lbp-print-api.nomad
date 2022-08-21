job "lbp-print-api" {
  datacenters = ["dc1"]

  group "lbp-print-api-group" {
    count = 1

    volume "lbp-print-api-cache" {
      type      = "host"
      read_only = false
      source    = "lbp-print-api-cache"
    }

    network {
      port  "lbp-print-api-starticport"{
        to = 5000
      }
      port "workerport" {
        to = 5000
      }
      port "redisport" {
        static = 6379
        to = 6379
      }
    }

    service {
      name = "lbp-print-api"
      port = "lbp-print-api-starticport"

      tags = [
        "traefik.enable=true",
        "traefik.http.routers.lbpprintapi-https.tls=true",
        "traefik.http.routers.lbpprintapi-https.rule=Host(`print.lombardpress.org`)",
        "traefik.http.routers.lbpprintapi-https.tls.certresolver=myresolver",
        "traefik.http.routers.lbpprintapi-https.tls.domains[0].main=print.lombardpress.org",
        "traefik.http.routers.lbpprintapi-http.rule=Host(`print.lombardpress.org`)",
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
      resources {
        memory = 800
        memory_max = 1000
      }
      config {
        image = "jeffreycwitt/lbp-print-api"
        volumes = [
          # needs to be lower case z and not Capital Z to get permissions correct in this case; I'm not sure why
          "/home/jcwitt/lbp-print-api-cache:/usr/src/app/cache:z"
        ]
        ports = ["lbp-print-api-starticport"]
        #command = "gunicorn -w 1 -b 0.0.0.0:5000 app:app"
        force_pull = true
      }
      env{
        REDIS_ENDPOINT="${NOMAD_IP_redisport}"
      }
    }
    task "queue-worker" {
      driver = "podman"
      resources {
        memory = 800
        memory_max = 1000
      }
      config {
        image = "jeffreycwitt/lbp-print-api"
        volumes = [
          # needs to be lower case z and not Capital Z to get permissions correct in this case; I'm not sure why
          "/home/jcwitt/lbp-print-api-cache:/usr/src/app/cache:z"
        ]
        ports = ["workerport"]
        force_pull = true
        command = "python3"
        args = ["worker.py"]
      }
      env{
        REDIS_ENDPOINT="${NOMAD_IP_redisport}"
      }
    }
    task "redis" {
      driver = "podman"
      resources {
        memory = 800
        memory_max = 1000
      }
      config {
        image = "redis:alpine"
        ports = ["redisport"]
      }
      #env{
      #  REDIS_ENDPOINT= "redis"
      #}
    }
  }
}