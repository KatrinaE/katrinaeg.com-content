# Ensure Python >= 3.9
python3 --version

# Install venv
sudo apt install python3.12-venv

# For some reason this doesn't work, so I'm calling Python manually below
source ./pelican-dev-env/bin/activate

# Install pelican
./pelican-dev-env/bin/python -m ensurepip --default-pip
./pelican-dev-env/bin/python -m pip install "pelican[markdown]"

# Generate input
vi content/keyboard-review.md

# Generate output
../pelican-dev-env/bin/python -m pelican content

# Write mini server for dev purposes

```package main

import (
	"log"
	"net/http"
)

func main() {
	fs := http.FileServer(http.Dir("./output"))
	http.Handle("/", fs)

	log.Print("Listening on :3000...")
	err := http.ListenAndServe(":3000", nil)
	if err != nil {
		log.Fatal(err)
	}
}
```
# Serve static files
go run main.go


# Note, Pelican has this importer tool, but I don't think it will work for pure HTML
https://docs.getpelican.com/en/latest/importer.html


# I used this theme
pushd ../pelican-dev-env/lib/python3.12/site-packages/pelican/themes/
git clone https://github.com/hamaluik/foundation-default-colours.git
echo "THEME = '../pelican-dev-env/lib/python3.12/site-packages/pelican/themes/foundation-default-colours'" > pelicanconf.py
../pelican-dev-env/bin/python -m pelican content -s pelicanconf.py


# Needed this to convert to markdown
../../../pelican-dev-env/bin/python -m pip install "html2text"
