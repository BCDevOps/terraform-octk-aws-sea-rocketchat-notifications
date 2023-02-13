terraform {
  required_providers {
    restapi = {
      source  = "fmontezuma/restapi"
      version = "1.14.1"
    }
  }
}

provider "restapi" {
  alias                = "restapi_headers"
  uri                  = "https://chat.developer.gov.bc.ca/"
  debug                = true
  write_returns_object = true

  headers = {
    X-Auth-Token = var.SECRET_TOKEN
    X-User-Id    = var.X-User-Id
    Content-Type = "application/json"
  }


}

# export TF_VAR_SECRET_TOKEN=$(some_special_thing_to_get_credential)

resource "restapi_object" "delete_channel" {
  provider     = restapi.restapi_headers
  path         = "/api/v1/channels.delete"
  id_attribute = var.ID
  object_id    = var.ID
  data         = <<EOF
{
  "roomName": "${var.name}",
  "id": "${var.ID}" 
  
}
EOF
}