# network.tf

locals {
  az_count = 2
}

resource "aws_vpc" "aegiscan" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "aegiscan-vpc"
  }
}

data "aws_availability_zones" "available" {}

resource "aws_subnet" "public" {
  count                   = local.az_count
  vpc_id                  = aws_vpc.aegiscan.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "aegiscan-public-subnet-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.aegiscan.id
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_vpc.aegiscan.main_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
}

resource "aws_eip" "gw" {
  count      = local.az_count
  domain     = "vpc"
  depends_on = [aws_internet_gateway.gw]
}

resource "aws_nat_gateway" "gw" {
  count         = local.az_count
  subnet_id     = aws_subnet.public[count.index].id
  allocation_id = aws_eip.gw[count.index].id
}

resource "aws_subnet" "private" {
  count             = local.az_count
  vpc_id            = aws_vpc.aegiscan.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "aegiscan-private-subnet-${count.index + 1}"
  }
}

resource "aws_route_table" "private" {
  count  = local.az_count
  vpc_id = aws_vpc.aegiscan.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.gw[count.index].id
  }
}

resource "aws_route_table_association" "private" {
  count          = local.az_count
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.aegiscan.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "aegiscan-public-rt"
  }
}

resource "aws_route_table_association" "public_subnet_routes" {
  count          = local.az_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public_rt.id
}
