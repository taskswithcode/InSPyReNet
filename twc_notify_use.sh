USAGE="<ip> <host> <name> <action> <dest>"
ip=${1?$USAGE}
host=${2?$USAGE}
name=${3?$USAGE}
action=${4?$USAGE}
dest=${5?$USAGE}
curl -d "{\"ip\":\"$ip\",\"name\":\"$name\",\"host\":\"$host\",\"action\":\"$action\"}" -H 'Content-Type: application/json' $dest &
