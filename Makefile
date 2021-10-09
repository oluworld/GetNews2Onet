all:
	true

obk:
	python2 obk.py > obk.`date +"%Y_%m%b%d_%H.%M.%S"`.alvo

print:
    bash print5.sh

.PHONY: all print obk
