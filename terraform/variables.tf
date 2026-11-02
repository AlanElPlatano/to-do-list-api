variable "region" {
  description = "Región de AWS donde se crearán los recursos"
  type        = string
  default     = "us-east-1"
}

variable "allowed_cidr" {
  description = "CIDR desde el que se permite SSH y acceso a la API"
  type        = string
  default     = "0.0.0.0/0"
}

variable "instance_type" {
  description = "Tamaño de la instancia EC2"
  type        = string
  default     = "t3.micro"
}

variable "project_name" {
  description = "Nombre del proyecto, se usa como prefijo en los recursos"
  type        = string
  default     = "todo-api"
}

variable "repo_url" {
  description = "Repositorio público que la instancia clona al arrancar"
  type        = string
  default     = "https://github.com/AlanElPlatano/to-do-list-api.git"
}

variable "app_port" {
  description = "Puerto en el que escucha la API"
  type        = number
  default     = 8000
}
