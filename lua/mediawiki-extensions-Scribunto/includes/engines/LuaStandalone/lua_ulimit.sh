#!/bin/sh

ulimit -St $1
ulimit -Ht $2
ulimit -v $3
eval "exec $4"

