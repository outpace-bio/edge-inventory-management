if [ $# -ne 2 ]; then
  echo 1>&2 "Usage: $0 COMPONENT-NAME COMPONENT-VERSION"
  exit 3
fi

COMPONENT_NAME=$1
VERSION=$2

# set artifact tags
FRONTEND_TAG=inventory-manager-webserver
BACKEND_TAG=inventory-manager-backend

# copy recipe to greengrass-build
cp recipe.yaml ./greengrass-build/recipes

# create custom build directory
rm -rf ./custom-build
mkdir -p ./custom-build/$COMPONENT_NAME

# build Docker images
cd src
docker-compose -f docker-compose.yaml build
cd ..

# save Docker images as tar
docker save --output ./custom-build/$COMPONENT_NAME/$FRONTEND_TAG.tar $FRONTEND_TAG
docker save --output ./custom-build/$COMPONENT_NAME/$BACKEND_TAG.tar $BACKEND_TAG

# include docker-compose.yaml in archive
cp src/docker-compose.yaml ./custom-build/$COMPONENT_NAME/

# include empty directories for each image build context
mkdir -p ./custom-build/$COMPONENT_NAME/backend
mkdir -p ./custom-build/$COMPONENT_NAME/frontend

# zip up archive
zip -r -X ./custom-build/$COMPONENT_NAME.zip ./custom-build/$COMPONENT_NAME

# copy archive to greengrass-build
cp ./custom-build/$COMPONENT_NAME.zip ./greengrass-build/artifacts/$COMPONENT_NAME/$VERSION/