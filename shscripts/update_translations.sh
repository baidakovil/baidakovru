#!/bin/bash

pybabel extract -F translations/babel.cfg -o translations/messages.pot .
pybabel update -i translations/messages.pot -d translations
echo "Now edit translations/*/LC_MESSAGES/messages.po files and run:"
echo "pybabel compile -d translations"