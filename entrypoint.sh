for i in {30..0}; do
    if curl elasticsearch:9200; then
     echo "Es started "
            break;
    fi
    sleep 2

