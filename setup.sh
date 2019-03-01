if [ $# -eq 0 ]
then
  echo "Usage: $0 <magma_dir>"
  exit 1
fi

cp supervisord.conf ${1}/orc8r/gateway/.
cp -r hello ${1}/orc8r/gateway/python/magma/.

mkdir -p ~/magma/certs
touch ~/magma/snowflake
