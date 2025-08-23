# 📊 Padrão de Dados CSV - Coleta de Repositórios GitHub

Este documento descreve a estrutura e significado dos dados coletados pelo script de análise de repositórios do GitHub.

## 📋 Estrutura do Arquivo CSV

O arquivo CSV gerado contém **26 colunas** organizadas em 4 categorias principais:

### 🔗 **Informações Básicas**
| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `nome` | String | Nome do repositório no GitHub | `freeCodeCamp` |
| `proprietario` | String | Nome do usuário ou organização | `freeCodeCamp` |
| `tipo_proprietario` | String | Tipo do proprietário | `Organization` ou `User` |
| `url` | URL | Link direto para o repositório | `https://github.com/freeCodeCamp/freeCodeCamp` |
| `homepage` | URL | Página oficial do projeto | `https://www.freecodecamp.org` |
| `descricao` | String | Descrição do projeto | `freeCodeCamp.org's open-source codebase...` |

### ⭐ **Métricas de Popularidade**
| Coluna | Tipo | Descrição | Significado |
|--------|------|-----------|-------------|
| `estrelas` | Integer | Número de estrelas | Indicador de popularidade |
| `forks` | Integer | Cópias do repositório | Adoção pela comunidade |
| `watchers` | Integer | Observadores | Interesse ativo no projeto |

### 📈 **Métricas de Atividade**
| Coluna | Tipo | Descrição | Significado |
|--------|------|-----------|-------------|
| `commits` | Integer | Total de commits | Atividade de desenvolvimento |
| `issues_abertas` | Integer | Issues abertas | Problemas pendentes |
| `issues_fechadas` | Integer | Issues fechadas | Problemas resolvidos |
| `prs_abertos` | Integer | Pull Requests abertos | Contribuições pendentes |
| `prs_fechados` | Integer | PRs fechados | Contribuições rejeitadas |
| `prs_mesclados` | Integer | PRs mesclados | Contribuições aceitas |
| `releases` | Integer | Versões lançadas | Maturidade do projeto |

### 🕒 **Informações Temporais**
| Coluna | Tipo | Formato | Descrição |
|--------|------|---------|-----------|
| `data_criacao` | DateTime | ISO 8601 | Data de criação do repositório |
| `ultima_atualizacao` | DateTime | ISO 8601 | Última modificação |
| `ultimo_push` | DateTime | ISO 8601 | Último commit |

### 💻 **Informações Técnicas**
| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `linguagem_principal` | String | Linguagem predominante | `TypeScript` |
| `todas_linguagens` | String | Lista de linguagens | `TypeScript; JavaScript; CSS; HTML` |
| `licenca` | String | Tipo de licença | `MIT License` |
| `tamanho_kb` | Integer | Tamanho em KB | `51200` |
| `branch_principal` | String | Branch principal | `main` |

### 🏷️ **Status e Metadados**
| Coluna | Tipo | Valores | Descrição |
|--------|------|---------|-----------|
| `arquivado` | Boolean | `Sim/Não` | Repositório arquivado |
| `eh_fork` | Boolean | `Sim/Não` | É uma cópia de outro repo |
| `eh_template` | Boolean | `Sim/Não` | Serve como template |
| `topicos` | String | Lista separada por `;` | Tags/tópicos do projeto |

nome,proprietario,tipo_proprietario,url,homepage,estrelas,descricao,forks,watchers,commits,issues_abertas,issues_fechadas,prs_abertos,prs_fechados,prs_mesclados,releases,data_criacao,ultima_atualizacao,ultimo_push,linguagem_principal,todas_linguagens,licenca,tamanho_kb,branch_principal,arquivado,eh_fork,eh_template,topicos

## 📊 Exemplos de Dados Reais

### 🎓 **Educação e Aprendizado**
**freeCodeCamp** - Plataforma de aprendizado de programação
- **380k estrelas** - Um dos repositórios mais populares
- **32k forks** - Alta adoção pela comunidade educacional
- **45k commits** - Desenvolvimento ativo contínuo
- **Foco**: Educação, JavaScript, React, Node.js

```csv
freeCodeCamp,freeCodeCamp,Organization,https://github.com/freeCodeCamp/freeCodeCamp,https://www.freecodecamp.org,380000,freeCodeCamp.org's open-source codebase and curriculum,32000,15000,45000,800,15000,200,5000,8000,150,2014-12-10T16:26:49Z,2024-01-15T20:30:00Z,2024-01-15T20:30:00Z,TypeScript,TypeScript; JavaScript; CSS; HTML,MIT License,51200,main,Não,Não,Não,freecodecamp; curriculum; javascript; react; nodejs
```

### 🎨 **Frameworks Frontend**
**Vue.js** - Framework JavaScript progressivo
- **210k estrelas** - Alta popularidade na comunidade
- **34k forks** - Forte adoção por desenvolvedores
- **28k commits** - Desenvolvimento ativo
- **Foco**: Frontend, JavaScript, Progressive Web Apps

```csv
vue,VueJS,Organization,https://github.com/vuejs/vue,https://vuejs.org,210000,Vue.js is a progressive, incrementally-adoptable JavaScript framework for building UI on the web,34000,12000,28000,400,8000,150,3000,5000,100,2013-07-29T10:58:51Z,2024-01-15T18:45:00Z,2024-01-15T18:45:00Z,JavaScript,JavaScript; TypeScript; CSS,MIT License,25600,main,Não,Não,Não,vue; framework; javascript; progressive; reactive
```

### 🧠 **Inteligência Artificial**
**TensorFlow** - Framework de machine learning do Google
- **180k estrelas** - Líder em IA/ML
- **85k forks** - Enorme adoção na comunidade científica
- **40k commits** - Desenvolvimento intensivo
- **Foco**: Machine Learning, Python, Deep Learning

```csv
tensorflow,google,Organization,https://github.com/tensorflow/tensorflow,https://tensorflow.org,180000,An Open Source Machine Learning Framework for Everyone,85000,25000,40000,1200,20000,300,8000,12000,200,2015-11-07T01:19:20Z,2024-01-15T17:10:00Z,2024-01-15T17:10:00Z,Python,Python; C++; JavaScript; Shell,Apache License 2.0,40960,main,Não,Não,Não,tensorflow; machine-learning; deep-learning; neural-networks; ai; ml
```

### 🛠️ **Ferramentas de Desenvolvimento**
**VS Code** - Editor de código da Microsoft
- **150k estrelas** - Editor mais popular
- **25k forks** - Forte comunidade de extensões
- **30k commits** - Desenvolvimento contínuo
- **Foco**: IDE, TypeScript, Electron, Extensibilidade

```csv
vscode,microsoft,Organization,https://github.com/microsoft/vscode,https://code.visualstudio.com,150000,Visual Studio Code,25000,12000,30000,800,15000,150,3000,5000,120,2014-11-18T18:54:33Z,2024-01-15T16:45:00Z,2024-01-15T16:45:00Z,TypeScript,TypeScript; JavaScript; CSS; HTML,MIT License,61440,main,Não,Não,Não,vscode; editor; ide; typescript; electron; microsoft
```