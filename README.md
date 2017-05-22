# Versioning Copy-On-Write File System (vCowFS)
### Assignment 2: Versioning Copy-On-Write File System (vCowFS)
This project was submitted to **Operating System subject, CE KMITL 2016**
# Task List

| Implemented?        | Commmand           |
| ------------- |:-------------:|
| :x:                    | On-time submission |
| :heavy_check_mark:                    | Compile an build |
| :x:                    | CoW FS Design |
| :x:                    | Versioning Design |
| :x:                    | Mount/Unmount FS |
| :x:                    | Open/create/close/delete/truncate a file |
| :x:                    | Create/remove/rename/delete a directory |
| :heavy_check_mark:                    | Chmod/chown a file or directory |
| :x:                    | Listing file and directory with name, size, date, owner |
| :x:                    | Listing file and directory with last modified date and time |
| :x:                    | Reading a file |
| :x:                    | Writing and fsync a file |
| :x:                    | Auto-versioning a file |
| :x:                    | Retrieve an old-version of a file |
| :x:                    | Retrieve the file on re-mounting |
| :x:                    | getattr(stat) |
| :heavy_check_mark:     | mkdir |
| :heavy_check_mark:     | rmdir |
| :heavy_check_mark:     | cd |
| :heavy_check_mark:     | chmod |
| :heavy_check_mark:     | chown |
| :heavy_check_mark:     | chgrp |


# Getting Started
### Install

on ubuntu 16.04

install pip and setuptools
```
  $ sudo apt-get install python3-pip
  $ pip3 install setuptools
```

install package
```
  $ sudo apt-get install libattr1-dev automake autotools-dev g++ git libcurl4-gnutls-dev libfuse-dev libssl-dev libxml2-dev make pkg-config
```

download llfuse 1.2 from pypi

```
  $ wget https://pypi.python.org/packages/95/0d/44117ac95b8b52ff5640690d622105d7afa0dd4354432e6460c589f6382c/llfuse-1.2.tar.bz2#md5=4bf20ec273bc2ca41c6f58e5f4d8989d
```

unpack it

```
  $ tar xvjf llfuse-1.2.tar.bz2
```

install it

```
  $ cd llfuse-1.2
  $ python3 setup.py build_ext --inplace
```
### Create an image file

```
  $dd if=/dev/zero of=storage.img bs=1M count=10
  $mkfs ntfs -F storage.img
```

# Run !!

```
  $ python3 vcowfs.py storage.img tmp 15
```

# Group Member
* Pongsatorn Wanitchinchai
* Pornchay Apichardpanth
* Patcharapon Jantana
* Peerawat Pipattanakulchai
* Supawit Kansompoj
* Suttichai Pongsanont
* Sirapat Tiyasuwan
* Siridej Phanathanate
* Atthasit Sintunyatum
* Isara Naranirattisai

# Reference

Will be available soon
