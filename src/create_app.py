import os, sys
import requests
import webbrowser
import argparse
import configparser
import logging
import json
import shutil
from slugify import slugify


class CreateApp:
    CLI_VERSION = "Create App v-1.0.0"
    INI_FILE = "autofile.ini"

    def __load_ini_file(self, filename):

        full_path = os.path.abspath(os.path.join("./src", filename))
        path_config_file = full_path if os.path.isfile(full_path) else \
            os.path.abspath(os.path.join(os.path.dirname(sys.executable), filename))
        self.config = configparser.ConfigParser()
        if self.config.read(path_config_file):
            return True
        else:
            logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename="errors.log")
            logging.error(f"Não foi possivel carregar o arquivo de coniguração em {path_config_file}")
            return False

    def __init__(self):
        if self.__load_ini_file(self.INI_FILE):
            self.__run__()

    def __run__(self):
        self.parser = argparse.ArgumentParser(
            prog="create-app",
            description="Criador rapido de projetos com configurações pre-definidas.",
            epilog="Desenvolvido por: Rafael do Carmo",
            usage="%(prog)s [options]")

        self.parser.version= self.CLI_VERSION
        self.parser.add_argument("-v", "--version", action="version")
        self.installed = []
        create_next_subparsers = self.parser.add_subparsers(help="Options for create Next Aplication")

        self.__create__next__parser(create_next_subparsers)

        parser_args = self.parser.parse_args()
        if len(vars(parser_args)) > 0:

            try: 
              self.project_name = slugify(parser_args.name, separator='-', lowercase=True)
              self.destination = os.path.abspath(os.path.join(parser_args.dest, self.project_name))
              if parser_args.auto:
                self.__auto_create_next_app()
              if not parser_args.auto:
                self.base_create_next()
                print("next")

              if len(parser_args.options) > 0:
                if('e' in parser_args.options):
                  self.add_eslint_importer()
                if('s' in parser_args.options):
                  self.add_styled_components()
                if('p' in parser_args.options):
                  self.add_plop()
            except Exception as e:
                print(f"Argumento inválido: {e}")
                sys.exit(1)
        else:
            self.parser.print_help()
            sys.exit(1)

    def __create__next__parser(self, subparsers):
        self.next_parser = subparsers.add_parser("create-next-app", help="Criador Next APP")
        self.next_parser.add_argument("-n", "--name", help="Name of project", type=str, default="next-app")
        self.next_parser.add_argument("-a", "--auto", help="Create next app with pre definition config", action="store_true")
        self.next_parser.add_argument("-d", "--dest", help="Set Personalizated destination", type=str, default=".")
        

        self.next_parser.add_argument("-o", "--options", help="""
         e: add eslint-import helper 
         s: add Styled Components 
         p: add Plop Generator """, type=str, default="")

    def __auto_create_next_app(self):
      self.base_create_next()
      self.add_eslint_importer()
      
      os.system("yarn add -D @commitlint/config-conventional @commitlint/cli")
      with open('commitlint.config.js', 'w') as commitlint:
        commitlint.write("{ module.exports = {extends: ['@commitlint/config-conventional']} }")
      
      # os.chdir(self.destination)
      self.add_styled_components()
      self.add_storybook()
      self.add_plop()
      self.add_material_ui()
      os.system("cls")
      [print(f"Instalado - {package}") for package in self.installed]
      os.system("code .")

    def base_create_next(self):
      print("Installing Next with prettier")

      os.system(f"yarn create next-app {self.project_name} --typescript")

      os.chdir(self.destination)
      try:
        with open('.eslintrc.json', 'r') as eslint:
          eslint_config = json.load(eslint)
      except Exception as e:
        os.system("yarn add -D eslint")
        os.system("yarn eslint --init")
        with open('.eslintrc.json', 'r') as eslint:
          eslint_config = json.load(eslint)

      


      with open('.editorconfig', 'w') as editor:
          editor.write(
          """root = true
          [*]
          indent_style = space
          indent_size = 2
          end_of_line = lf
          charset = utf-8
          trim_trailing_whitespace = true
          insert_final_newline = true""")

      eslint_config["rules"] = dict()
      eslint_config["rules"]["react/prop-types"] = "off"
      eslint_config["rules"]["react/react-in-js-scope"] = "off"
      eslint_config["rules"]["@typescript-eslint/explicit-module-boundary-types"] = "off"

      eslint_config["settings"] = {"react" :{ "version": "detect"} }
      
      eslint_config['extends'] = list()
      eslint_config['extends'].append("next/core-web-vitals")
      eslint_config['extends'].append("plugin:prettier/recommended")
      eslint_config['plugins'] = list()

      os.system('yarn add eslint-plugin-react@latest @typescript-eslint/eslint-plugin@latest @typescript-eslint/parser@latest -D')
      os.system('yarn add eslint-plugin-react-hooks --dev')

      prettierConfig = {
          "trailingComma": "none",
          "semi": False,
          "singleQuote": True
      }

      with open('.prettierrc', 'w') as prettier:
          json.dump(prettierConfig, prettier, indent=4)

      os.system('yarn add --dev --exact prettier')

      os.system('yarn add -D eslint-plugin-prettier eslint-config-prettier')

      os.makedirs('.vscode')

      vscodeSettings = {
      "editor.formatOnSave": False,
      "editor.codeActionsOnSave": {"source.fixAll.eslint": True}
      }



      with open('.eslintrc.json', 'w') as eslint:
          json.dump(eslint_config, eslint, indent=4)
      with open('.vscode/settings.json', 'w') as vscode:
          json.dump(vscodeSettings, vscode, indent= 4)

      os.makedirs(os.path.join("src", "pages")) 
      shutil.rmtree("pages")
      shutil.rmtree("styles")
      with open('tsconfig.json', 'r') as tsconfig:
        tsconfig_json = json.load(tsconfig)

      tsconfig_json['compilerOptions']['baseUrl'] = "src"
      with open('tsconfig.json', 'w') as tsconfig:
        json.dump(tsconfig_json, tsconfig, indent=4)

      
      print(f"* - Next installation finished {' '*10}", end="\r")

    def add_eslint_importer(self):
      #add eslint-import helper
      print("Installing eslint-import helper", end="\r")
      os.system('yarn add -D eslint-plugin-import-helpers')
      with open(".eslintrc.json", 'r') as eslint:
        eslint_config = json.load(eslint)

      eslint_inporter_rules = {
        'import-helpers/order-imports': [
            'warn',
            {"newlinesBetween": 'always',
                "groups": [
                    'module',
                    '/^@shared/',
                    ['parent', 'sibling', 'index'],
                ],
                "alphabetize": { "order": 'asc', "ignoreCase": True },
            },
        ]}
      
      eslint_config['plugins'].append('eslint-plugin-import-helpers')
      eslint_config['rules']['import-helpers/order-imports'] = eslint_inporter_rules['import-helpers/order-imports']

      with open(".eslintrc.json", 'w') as eslint:
        json.dump(eslint_config, eslint, indent=4)
      self.installed.append("Eslint")
      print("* Eslint-import-helper Installation Finished")

    def create_file_by_text_fromUrl(self, url, name_file, folder='.', secondary_url = False):
      file_document = requests.get(url)
      if (file_document.status_code == 200):
        with open(os.path.join(folder, name_file), 'w') as document:
          document.write(file_document.text)
      else:
        print(f'Erro ao pegar arquivo {name_file} - favor criar o arquivo manualmente')
        if(secondary_url):
          webbrowser.open(secondary_url)


    def add_styled_components(self):
      os.system("yarn add -D @types/styled-components babel-plugin-styled-components")
      try:
        with open('.babelrc', 'r') as babel_file:
          babel_config = json.load(babel_file)
      except Exception as e:
        babel_config = dict()
      
      babel_config["presets"] = ["next/babel", "@babel/preset-typescript"]
      babel_config['plugins'] = [["babel-plugin-styled-components", {"ssr": True, "displayName": True}]]
      babel_config['env'] = {"test": {"plugins": [ [ "babel-plugin-styled-components", { "ssr": False, "displayName": False}]]}}
      with open('.babelrc', 'w') as babel_file:
        json.dump(babel_config, babel_file, indent=4)

      os.system("yarn add styled-components")

      self.create_file_by_text_fromUrl(\
        url='https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/_document.tsx',
        folder=os.path.join('src', 'pages'),
        name_file='_document.tsx',
        secondary_url='https://github.com/vercel/next.js/blob/main/examples/with-styled-components/pages/_document.js'
      )
      
      self.create_file_by_text_fromUrl(\
        url='https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/_app.ts',
        folder=os.path.join('src', 'pages'),
        name_file='_app.tsx'
      )

      os.makedirs(os.path.join('src', 'styles'))

      global_styles = requests.get('https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/global.ts')
      if(global_styles.status_code == 200):
        global_styles = global_styles.text
      else:
        global_styles = """ 
          import { createGlobalStyle } from 'styled-components'

          const GlobalStyles = createGlobalStyle`
          * {
            padding: 0;
            margin: 0;
            box-sizing: border-box;
          }
          a {
            text-decoration: none;
          }

          html{
            font-size: 62.5%;
          }

          body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif
            }

          `
          export default GlobalStyles
        """
      with open(os.path.join('src', 'styles', 'global.ts'), 'w') as global_styles_file:
        global_styles_file.write(global_styles)
      

      theme = requests.get('https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/theme.ts')

      if(theme.status_code == 200):
        theme = theme.text
      else:
        print(f'Url from theme error - {theme.status_code}')
        theme="""export default {} """

      with open(os.path.join('src', 'styles', 'theme.ts'), 'w') as theme_file:
        theme_file.write(theme)
      
      with open('styled-components.d.ts', 'w') as styled_components_d_ts:
        styled_components_d_ts.write(\
        """
        import theme from 'styles/theme'

        type Theme = typeof theme

        declare module 'styled-components' {
          // eslint-disable-next-line @typescript-eslint/no-empty-interface
          export interface DefaultTheme extends Theme {}
        }
        """)

      self.installed.append("Styled Components")

    def add_storybook(self):

      os.system('npx sb init')
      self.create_file_by_text_fromUrl(\
        url='https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/main.js',
        folder=os.path.join('.storybook'),
        name_file='main.js'
      )
      shutil.rmtree(os.path.join('src', 'stories'))
      self.installed.append("Storybook")

    def add_plop(self):
      os.chdir(self.destination)
      os.system("yarn add -D plop")
      os.makedirs(os.path.join("generators", "templates"))
      self.create_file_by_text_fromUrl(\
        url="https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/plolpfile.js",
        folder=os.path.join("generators"),
        name_file="plopfile.js"
      )
      self.create_file_by_text_fromUrl(\
        url="https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/plop_templates/Component.tsx.hbs",
        folder=os.path.join("generators", "templates"),
        name_file="Component.tsx.hbs"
      )
      self.create_file_by_text_fromUrl(\
        url="https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/plop_templates/stories.tsx.hbs",
        folder=os.path.join("generators", "templates"),
        name_file="stories.tsx.hbs"
      )
      self.create_file_by_text_fromUrl(\
        url="https://raw.githubusercontent.com/rafa-carmo/public_files/main/next/plop_templates/styles.ts.hbs",
        folder=os.path.join("generators", "templates"),
        name_file="styles.ts.hbs"
      )

      with open("package.json", 'r') as package:
        package_json = json.load(package)

      package_json["scripts"]["generate"] = "yarn plop --plopfile generators/plopfile.js"

      with open("package.json", 'w') as package:
        json.dump(package_json, package, indent=4)
      self.installed.append("Plop")

    def add_material_ui(self):
      os.system("yarn add @mui/material @emotion/react @emotion/styled")
      if("Styled Component" in self.installed):
        os.system("yarn add @mui/styled-engine")
        with open("package.json", 'r') as package:
          package_json = json.load(package)
        package_json['alias']= {
          "@mui/styled-engine": "@mui/styled-engine-sc"
        }
        with open("package.json", 'w') as package:
          json.dump(package_json, package, indent=4)

      self.installed.append("Material UI")
