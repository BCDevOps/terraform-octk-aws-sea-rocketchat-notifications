terraform {
  required_providers {
    restapi = {
      source = "fmontezuma/restapi"
      version = "1.14.1"
    }
  }
}
module "Deletechannel" {
    source = "../Delete-module"
    ID = var.ID
    X-User-Id = var.X-User-Id
    name = var.name1
    SECRET_TOKEN = var.SECRET_TOKEN

}

module "Createchannel1" {
    source = "../Delete-module"
    ID = var.ID1
    X-User-Id = var.X-User-Id
    name = var.name2
    SECRET_TOKEN = var.SECRET_TOKEN

}