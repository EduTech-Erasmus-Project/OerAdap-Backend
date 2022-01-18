from pysbd.utils import PySBDFactory #Para separar oraciones
from bs4 import BeautifulSoup #Para obtener el contenido html
import nltk #para hacer analisis de gramatica
import roman #para trnasformar numeros romanos
import spacy
from datetime import datetime
from googletrans import Translator
import math
import numpy as np
import re
from sklearn.datasets import load_files
nltk.download('stopwords')
import pickle
from nltk.corpus import stopwords
import pandas as pd
import stanza
stanza.download('es')  
import json
import calendar
import roman 
import torch
from transformers import BertForMaskedLM, BertTokenizer
import requests

def easy_reading(text_content):
    """
    Metodo para adaptacion de lectura facil.
    :param text_content: Parrafo en formato html.
    :return: Retorno un string de una etiqueta parrafo en html.
    """

    text_content = adaptar_texto(text_content)

    return text_content

def video_transcript(path_video):
    transcripts = []
    captions = []

    return transcripts, captions

def image_description(nose_sabe_todavia):
    img_desciption = "automatic description"
    return img_desciption






####### Metodos para LF

diccionario_abreviaturas = {'Ed.':'Educacion','a.C':'Antes de Cristo'}

"""Diccionario de numeros cardinales"""

def convertir_ordinales(numero_texto):

  Unidad = ["", "primero", "segundo", "tercero",
        "cuarto", "quinto", "sexto", "septimo", "octavo", "noveno"]
  Decena=["", "decimo", "vigesimo", "trigesimo", "cuadragesimo",
        "quincuagesimo", "sexagesimo", "septuagesimo", "octogesimo", 
        "nonagesimo"]
  Centena=["", "centesimo", "ducentesimo", "tricentesimo",
        " cuadringentesimo", " quingentesimo", " sexcentesimo",
        " septingentesimo"," octingentesimo", " noningentesimo"]
  N=int(numero_texto)
  u= N % 10
  d=int(math.floor(N/10))%10
  c=int(math.floor(N/100))
  if(N>=100): 
    numero_texto=Centena[c]+" "+Decena[d]+" "+Unidad[u]
  
  else:
    if(N>=10):
      numero_texto= Decena[d]+" "+Unidad[u]

    else:
      numero_texto = Unidad[N]
    
  return numero_texto

"""Adaptar Textos"""

texto_html= 'El numero V y el numero X son en numeros romanos. El 11/05/2021 fueron a la cena 5 personas : Marcos, el papá; Marcela, la mamá; Juan, el hermano; Sofía, la prima; Sandra, la hermana; y Cristina, la novia. Banco/préstamo de libros de manera sistemática y voluntaria en los cursos de 3º a 6º de Ed. Primaria: Lengua, Matemáticas, Conocimiento del Medio I, Inglés XI, Música y Religión. Con la finalidad de que 5000 familias ahorren una cantidad significativa en la adquisición de los libros. Es un programa que ha entrañado dificultades de organización y realización pero estamos muy satisfechos de los resultados. En 1º y 2º curso de Primaria y en Ed. Infantil no es posible implantar este programa puesto que es material fungible, y apenas tiene utilidad de un curso para el siguiente. Los libros fueron recibidos por los niños durante la jornada estudiantil.'



def adaptar_texto(texto):

  texto_nuevo=""
  texto_auxiliar1=""
  texto_auxiliar2=""

  # 1. Eliminar abreviaturas
  texto=eliminar_abreviaturas(texto)
  
  # 2. Eliminar numeros cardinales
  palabras = texto.split(sep=" ")
  for i in palabras:
    if i.find("º")!=-1:
      i= i.replace("º","")
      i=convertir_ordinales(i)
   
    
    

    
    texto_nuevo=texto_nuevo+i+" "

  #
  
  texto=texto_nuevo
  # . Separar en oraciones
  oraciones = obtener_oraciones(texto)

  #Eliminar los puntos suspensivos y el punto y coma
  for i in range(len(oraciones)):
    texto_auxiliar1=eliminar_punto_coma(str(oraciones[i]))
    if(texto_auxiliar1!=None):
      oraciones[i]=texto_auxiliar1

  # . Convertir en lista los items
  for i in range(len(oraciones)):
    texto_auxiliar2=generar_listas(str(oraciones[i]))
    if(texto_auxiliar2!=None):
      oraciones[i]=texto_auxiliar2




  

  #Escribir y redonder cifras
  for i in range(len(oraciones)):
    oraciones[i]=redondear_cifras(str(oraciones[i]))


  #Adaptar fechas
  
  for i in range(len(oraciones)):
    texto_nuevo=""
    palabras=oraciones[i].split()
    for j in range(len(palabras)):
      if isFecha(palabras[j]):
        palabras[j]=adaptar_fechas(palabras[j])
      texto_nuevo=texto_nuevo+palabras[j]+" "
    #texto_nuevo=texto_nuevo+j+" "
    oraciones[i]=texto_nuevo


    #adaptar numeros romanos
    for i in range(len(oraciones)):
      texto_nuevo=""
      palabras=oraciones[i].split()
      print(palabras)
      for j in range(len(palabras)):
        
        palabras[j]=str(adaptar_numeros_romanos(palabras[j]))
        texto_nuevo=texto_nuevo+palabras[j]+" "
      #texto_nuevo=texto_nuevo+j+" "
      oraciones[i]=texto_nuevo
    








  print("termina")
    
  return oraciones



"""Covertir fechas """

def adaptar_fechas(fecha_texto):

  print(fecha_texto)

  dias = ['Lunes','Martes','Miercoles','Jueves', 'Viernes', 'Sabado', 'Domingo']
  meses = ['','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
  dia=""
  fecha=""

  
  if len(fecha_texto.split("/"))!=0:
    
    elementos_fecha=fecha_texto.split("/")
   
    if(len(elementos_fecha[0])==2):
      
      fecha= datetime.strptime(fecha_texto, '%d/%m/%Y')
    else:
      
      if(len(elementos_fecha[0])==4):
        
        fecha= datetime.strptime(fecha_texto, '%Y/%m/%d')
  else:
    
    elementos_fecha=fecha_texto.split("-")
    if(len(elementos_fecha[0])==2):
      fecha= datetime.strptime(fecha_texto, '%d-%m-%Y')
    else:
      fecha= datetime.strptime(fecha_texto, '%Y-%m-%d')
    
  print(elementos_fecha)

  dia= str(calendar.day_name[fecha.weekday()])
  dia_nombre=traducir(dia, 'es')
  dia_numero=str(fecha.day)

  mes=str(calendar.month_name[fecha.month])
  mes_nombre=traducir(mes,'es')

  anio=str(fecha.year)

  fecha_adaptada=dia_nombre+" "+dia_numero+" de "+ mes_nombre+" de "+ anio
  fecha_adaptada=fecha_adaptada.capitalize()


  
  return fecha_adaptada

def isFecha(fecha):
  if len(fecha.split(sep="-"))==3 :
    return True
    
  if len(fecha.split(sep="/"))==3 :
    return True
     
  return False

"""Eliminar Abreviaturas"""

def eliminar_abreviaturas(texto):

  texto = texto

  for abreviatura in diccionario_abreviaturas:
    texto=texto.replace(str(abreviatura),diccionario_abreviaturas[str(abreviatura)])

  return texto

"""Metodo para separar las oraciones"""

def obtener_oraciones(texto):

  nlp = spacy.blank('es')
  nlp.add_pipe(PySBDFactory(nlp))
  doc = nlp(texto)
  lista = (list(doc.sents))
  return lista

"""Eliminar punto y coma y puntos suspensivos"""

def eliminar_punto_coma(oracion):

  inicio=0
  fin=0
  texto_final=""

  inicio=int(oracion.find(':'))
  fin=int(len(oracion))
  if(oracion.find(':')!=-1)and(oracion.find(";")!=-1):
    texto_a_remplazar=oracion[inicio+1:fin]

    elementos=(oracion[inicio+1:fin].strip().split(sep=";"))
    for elemento in elementos:

      inicio_coma=elemento.find(",")
      texto_borrable=elemento[int(inicio_coma):int(len(elemento))]
      elemento=elemento.replace(texto_borrable,",")

      texto_final = texto_final+elemento+" "

    oracion=oracion.replace(texto_a_remplazar,texto_final)
    return oracion
  return oracion

"""Convertir en lista los items

"""

def generar_listas(oracion):

  inicio=0
  fin=0

  inicio=int(oracion.find(':'))
  fin=int(len(oracion))
  if(oracion.find(':')!=-1):
    elementos=(oracion[inicio+1:fin].strip().split())
    texto_a_remplazar = oracion[inicio+1:fin]

    nuevo_texto= '<ul>'
    texto_elementos=''
    for elemento in elementos:
      texto_elementos= texto_elementos+'<li>'+elemento.capitalize()+'</li>' 
    texto_final=nuevo_texto+texto_elementos+'</ul>'
    texto_final = oracion.replace(texto_a_remplazar, texto_final)
    return texto_final

"""Escribir y redondear cifras"""

def redondear_cifras(oracion):


  texto_auxiliar=""
  elementos = oracion.split(sep=" ")
  for elemento in elementos:
    elemento=elemento.replace(".","")
    elemento=elemento.replace(",","")
    if(elemento.isdigit()):
      if(int(elemento))<=100:
        elemento="muy pocos"
        continue
      if(int(elemento)>100 and int(elemento)<=500):
        elemento="pocos"
        continue
      if(int(elemento)>500 and int(elemento)<=1000):
        elemento="varios"
        continue
      if(int(elemento)>1000 and int(elemento)<=3000):
        elemento="muchos"
        continue
      if(int(elemento)>3000) :
        elemento="bastantes"
        continue
    texto_auxiliar=texto_auxiliar+elemento+" "
  oracion=texto_auxiliar
  return oracion

"""adaptar numeros romanos"""

def adaptar_numeros_romanos(palabra):
  print("nuermos romanos")
  try:
    n=roman.fromRoman(palabra)
    print(n)
    return n
  except:
    return palabra









"""Adaptaciones gramaticales"""

#metodo para obtener los detalles de cada palabra en una oracion
def obtener_detalles(oracion):
 
  doc = nlp(str(oracion))
  lista=doc.sentences[0].to_dict()
  
  return lista

#obtener el txt de las frecuencias

data = pd.read_excel("palabras_frecuentes.xlsx", header=None)
datos=data.to_dict(orient='split')
diccionario_apoyo=dict(datos['data'])
diccionario_palabras={}
print(diccionario_apoyo)
for elemento in diccionario_apoyo:
  diccionario_palabras[str(elemento).strip()]=diccionario_apoyo[elemento]

diccionario_palabras

print(diccionario_palabras['a'])

print(predicciones_palabras)

#metodo para actualizar palabras
def adaptar_palabras(oracion):
  lista_palabras=obtener_detalles(oracion)
  palabras_a_cambiar =[]
  palabras_a_cambiar_limpias=[]
  nuevas_palabras=[]
  oracion_inicio = "[CLS] "
  oracion_final = " [SEP]"
  
  texto = oracion_inicio +  oracion + oracion_final 
  vector_palabras=[]
  indice=0



  #obtener palabras que son candidatas a cambiar
  for i in range(len(lista_palabras)):
    try:
      if lista_palabras[i]['upos']=="NOUN" or lista_palabras[i]['upos']=="VERB" or lista_palabras[i]['upos']=="ADV" or lista_palabras[i]['upos']=="ADJ"   :
        palabras_a_cambiar.append(lista_palabras[i]['text'])
    except:
      continue
      print("Error en el metodo de adaptar palabras")


  ##### remplazar las palabras usando beto
  for palabra in palabras_a_cambiar:
    auxiliar_palabra=""
    auxiliar_frecuencia=0
    auxiliar_palabra=palabra
    try:
      auxiliar_frecuencia=diccionario_palabras[str(palabra)]
    except: 
      print("no exsite esa palabra")
    print("cambiando la palabra:", palabra)  
    texto=texto.replace(palabra, '[MASK]',1)
    print("texto convertido: ",texto)

    print(auxiliar_palabra, " ", auxiliar_frecuencia)

    

    tokens = tokenizer.tokenize(texto)
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokens)
    tokens_tensor = torch.tensor([indexed_tokens])

     
    valor=tokens.index('[MASK]')
    
    print("posicion de la palabra", valor)
    masked_indxs=(valor,)

    predictions = model(tokens_tensor)[0]




    for k,midx in enumerate(masked_indxs):

      idxs = torch.argsort(predictions[0,midx], descending=True)
      predicted_token = tokenizer.convert_ids_to_tokens(idxs[:5])
      predicciones_palabras=predicted_token
      print(predicciones_palabras)
      #print('MASK',k,':',predicted_token)

    ### obtener los sinonimos de la palabra a tratar
    
    
    url='http://www.wordreference.com/sinonimos/'

    sinonimos=[]
    sinonimos_completos=[]
    buscar=url+palabra
    print(buscar, "url de busqueda")
    resp=requests.get(buscar)
    bs=BeautifulSoup(resp.text,'lxml')
    lista=bs.find_all(class_='trans clickable')
    for sin in lista:
        sino=sin.find_all('li')
      
        for fin in sino:
      
          fin=str(fin).replace("<li>","")
          fin=str(fin).replace("</li>","")
     
          sinonimos=fin.split(sep=",")
          for k in sinonimos:
            sinonimos_completos.append(k.strip())


      
        

    ###trabajar solo con sinonimos y con las palabras generadas por BETO
    palabras_en_comun=[]

    for sinonimo in sinonimos_completos:

      if sinonimo in predicciones_palabras:
        palabras_en_comun.append(sinonimo)
    
    print("sinonimos obtenidos web", sinonimos_completos)

    print("Palabras en comun", palabras_en_comun)

    if len(sinonimos_completos)!=0:
      print("entra", palabras_comunes)
      predicciones_palabras=palabras_en_comun
    else:
      predicciones_palabras=predicciones_palabras


    print("aqui se analiza", predicciones_palabras)


    for sugerencia in predicciones_palabras:
      try:
        if(diccionario_palabras[str(sugerencia)]>auxiliar_frecuencia):
          auxiliar_palabra=sugerencia
          auxiliar_frecuencia=diccionario_palabras[str(sugerencia)]
          print("Este es nmayor", auxiliar_palabra, auxiliar_frecuencia)
      except:
        continue


    texto=texto.replace("[MASK]", auxiliar_palabra)
    texto=texto.replace("[CLS]", "")
    texto=texto.replace("[SEP]", "")
    texto=texto.strip()

    



    


  
  return texto

url='http://www.wordreference.com/sinonimos/'
enlace=input("palabra a buscar: ")
sinonimos=[]
sinonimos_completos=[]
buscar=url+enlace
resp=requests.get(buscar)
bs=BeautifulSoup(resp.text,'lxml')
lista=bs.find_all(class_='trans clickable')
for sin in lista:
    sino=sin.find_all('li')
    print(sino, "sino")
    for fin in sino:

      print("Nuevbo," ,fin)
      fin=str(fin).replace("<li>","")
      fin=str(fin).replace("</li>","")
      print("va",fin)
      sinonimos=fin.split(sep=",")
      print("asi van los sinonimos", sinonimos)
      for k in sinonimos:
        sinonimos_completos.append(k.strip())


    
    
sinonimos_completos

oracion="El balance de caja resulto ser erróneo esta tarde."

adaptar_palabras(oracion)

"""Corregir oraciones en tiempo pasivo"""

dataset_pas = pd.read_csv('dataset.csv', sep=';', encoding='latin-1')
X, y = dataset_pas['oracion'], dataset_pas['tipo']

print(dataset_pas)



import string
punctuation = set(string.punctuation)
def tokenize(sentence):
    tokens = []
    for token in sentence.split():
        new_token = []
        for character in token:
            if character not in punctuation:
                new_token.append(character.lower())
        if new_token:
            tokens.append("".join(new_token))
    return tokens

from sklearn.feature_extraction.text import CountVectorizer
demo_vectorizer = CountVectorizer(
    tokenizer = tokenize,
    binary = True
)

from sklearn.model_selection import train_test_split
train_text, test_text, train_labels, test_labels = train_test_split(dataset_pas['oracion']
                                                                    , dataset_pas['tipo'],
                                                                    stratify=dataset_pas['tipo'])
print(f"Training examples: {len(train_text)}, testing examples {len(test_text)}")

real_vectorizer = CountVectorizer(tokenizer = tokenize, binary=True)
train_X = real_vectorizer.fit_transform(train_text)
test_X = real_vectorizer.transform(test_text)
from sklearn.svm import LinearSVC
classifier = LinearSVC()
classifier.fit(train_X, train_labels)
LinearSVC(C=1.0, class_weight=None, dual=True, fit_intercept=True,
          intercept_scaling=1, loss='squared_hinge', max_iter=1000,
          multi_class='ovr', penalty='l2', random_state=None, tol=0.0001,
          verbose=0)

nlp = stanza.Pipeline('es')

from sklearn.metrics import accuracy_score
predicciones = classifier.predict(test_X)
accuracy = accuracy_score(test_labels, predicciones)
print(f"Accuracy: {accuracy:.4%}")

#Listado de verbos para conversion

import pprint
with open('esp_verbos.json') as a:
    verbos_diccionario = json.load(a)

"""metodo para obtener el verbo en tiempo activo"""

def obtener_verbo_activo(sujeto,tiempo, verbo):
  for i in range(len(verbos_diccionario)):
    if str(verbos_diccionario[i]['verbo'])==verbo:
      verbo=str(verbos_diccionario[i]['indicativo']['preterito']['ellos/ellas/Uds.']).split()[1]
      print(verbos_diccionario[i]['indicativo']['preterito']['ellos/ellas/Uds.'])
  return verbo

def verificar_oracion_activa(oracion):

  agente1=""
  agente2=""
  accion=""
  
  pruebas=[]
  print(oracion)
  pruebas.append(oracion)
  
  frasesX=real_vectorizer.transform(pruebas)
  predicciones= classifier.predict(frasesX) 
  print(predicciones)
  if(predicciones=='active'):
    
    
    
    doc = nlp(str(oracion))
    print(doc.sentences[0])
    lista=doc.sentences[0].to_dict()
    print(lista[3])
    for i in range(len(lista)):
      if(lista[0]['upos'].lower()=='det'):
        
        agente2=str(lista[0]['text'])+str(lista[lista[0]['head']-1]['text'])

      if(lista[i]['deprel'].lower()=='obj'):
        agente1=str(lista[i-1]['text'])+" "+str(lista[i]['text'])

      if(lista[i]['deprel'].lower()=='root'):
        accion= obtener_verbo_activo('persona','indicativo',lista[i]['lemma'])
        print("verbo",accion)

    oracion= agente1 +" "+ accion +" " + agente2
    print(oracion)

verificar_oracion_activa("Es un programa que ha entrañado dificultades de organización y realización pero estamos muy satisfechos de los resultados.")

"""Deteccion de oraciones coordinadas y suboordinadas"""

dataset = pd.read_csv('dataset_sc.csv', sep=';', encoding='latin-1')
X, y = dataset['oracion'], dataset['tipo']

import string
punctuation = set(string.punctuation)
def tokenize(sentence):
    tokens = []
    for token in sentence.split():
        new_token = []
        for character in token:
            if character not in punctuation:
                new_token.append(character.lower())
        if new_token:
            tokens.append("".join(new_token))
    return tokens

from sklearn.feature_extraction.text import CountVectorizer
demo_vectorizer = CountVectorizer(
    tokenizer = tokenize,
    binary = True
)

from sklearn.model_selection import train_test_split
train_text, test_text, train_labels, test_labels = train_test_split(dataset['oracion']
                                                                    , dataset['tipo'],
                                                                    stratify=dataset['tipo'])
print(f"Training examples: {len(train_text)}, testing examples {len(test_text)}")

real_vectorizer = CountVectorizer(tokenizer = tokenize, binary=True)
train_X = real_vectorizer.fit_transform(train_text)
test_X = real_vectorizer.transform(test_text)
from sklearn.svm import LinearSVC
classifier = LinearSVC()
classifier.fit(train_X, train_labels)
LinearSVC(C=1.0, class_weight=None, dual=True, fit_intercept=True,
          intercept_scaling=1, loss='squared_hinge', max_iter=1000,
          multi_class='ovr', penalty='l2', random_state=None, tol=0.0001,
          verbose=0)

from sklearn.metrics import accuracy_score
predicciones = classifier.predict(test_X)
accuracy = accuracy_score(test_labels, predicciones)
print(f"Accuracy: {accuracy:.4%}")

pruebas=[]
pruebas.append("el espectaculo ya comenzo y el actor principal aun no ha llegado")
pruebas.append("El árbol que está junto a la puerta es un peral.")

frasesX=real_vectorizer.transform(pruebas)
predicciones= classifier.predict(frasesX)

print(predicciones)

"""Alternativas a palabras complejas"""









"""Metodo para traducir"""

def traducir(texto,destino):
  translator=Translator()
  traduccion=translator.translate(texto, dest=destino)
  return traduccion.text

"""Resultados"""

texto_final=adaptar_texto(texto_html)
texto=""
for i in texto_final:
  texto=texto + str(i) +"\n"

print(texto)





"""Adaptaciones lexicas"""

# entrenar a la red beto para obtener sinonimos
tokenizer = BertTokenizer.from_pretrained("pytorch/", do_lower_case=False)
model = BertForMaskedLM.from_pretrained("pytorch/")
e = model.eval()

# Now test it

text = "[CLS] Para solucionar los [MASK] de Chile, el presidente debe [MASK] de inmediato. [SEP]"
masked_indxs = (4,11)

tokens = tokenizer.tokenize(text)
indexed_tokens = tokenizer.convert_tokens_to_ids(tokens)
tokens_tensor = torch.tensor([indexed_tokens])

predictions = model(tokens_tensor)[0]

for i,midx in enumerate(masked_indxs):
    idxs = torch.argsort(predictions[0,midx], descending=True)
    predicted_token = tokenizer.convert_ids_to_tokens(idxs[:5])
    print('MASK',i,':',predicted_token)

for i,midx in enumerate(masked_indxs):
    print('MASK',i,':',midx)

def palabras_comunes(oracion):
  print("Oracion original", oracion)





"""pruebas"""

oracion= "La enfermedad se propaga principalmente de persona a persona a través de las gotículas que salen despedidas de la nariz o la boca de una persona infectada al toser, estornudar o hablar."

adaptar_palabras(oracion)

obtener_detalles(oracion)



adaptar_texto(texto_html)

"""Red Neuronal general para identificar las oraciones"""

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score

dataset_general = pd.read_csv('dataset_general.csv', sep=';', encoding='latin-1')

punctuation = set(string.punctuation)

def tokenize(sentence):
    tokens = []
    for token in sentence.split():
        new_token = []
        for character in token:
            if character not in punctuation:
                new_token.append(character.lower())
        if new_token:
            tokens.append("".join(new_token))
    return tokens



demo_vectorizer = CountVectorizer(
    tokenizer = tokenize,
    binary = True
)

train_text, test_text, train_labels, test_labels = train_test_split(dataset_general['oracion']
                                                                    , dataset_general['tipo'],
                                                                    stratify=dataset_general['tipo'])
print(f"Training examples: {len(train_text)}, testing examples {len(test_text)}")

real_vectorizer = CountVectorizer(tokenizer = tokenize, binary=True)
train_X = real_vectorizer.fit_transform(train_text)
test_X = real_vectorizer.transform(test_text)


classifier = LinearSVC()
classifier.fit(train_X, train_labels)
LinearSVC(C=1.0, class_weight=None, dual=True, fit_intercept=True,
          intercept_scaling=1, loss='squared_hinge', max_iter=1000,
          multi_class='ovr', penalty='l2', random_state=None, tol=0.0001,
          verbose=0)


predicciones = classifier.predict(test_X)
accuracy = accuracy_score(test_labels, predicciones)
print(f"Accuracy: {accuracy:.4%}")


pruebas=[]
pruebas.append("el espectaculo ya comenzo y el actor principal aun no ha llegado")
pruebas.append("El árbol que está junto a la puerta es un peral.")
pruebas.append("La tesis fue escrita por dos chicos de la carrera")

frasesX=real_vectorizer.transform(pruebas)
predicciones= classifier.predict(frasesX) 

print(predicciones)

"""Metodo para unir al proyecto Edutech"""

html='<p class="p-coJNpKLt"><span style="font-size: medium;">En los archivos adjuntos se encontrará el proceso realizado para el diseño de un circuito para la alarma de un automóvil: consideraciones iniciales, tabla de verdad, mapa de Karnaugh y circuito elaborado en el simulador Logisim.  El archivo PDF contiene la información escrita, mientras que el video presenta el proceso completo incluido la elaboración del circuito en el protoboard para verificar su funcionamiento correcto.</span></p>'

etiquetas_html=[]
while html.find(">")!=-1:

  posicion_inicio=html.find("<")
  posicion_fin=html.find(">")

  texto_remplazable=html[posicion_inicio:posicion_fin+1]
  etiquetas_html.append(texto_remplazable)
  print(texto_remplazable)
  html=html.replace(texto_remplazable," NOADAPTAR. ") 

  print(html)

print(etiquetas_html)

for etiqueta in etiquetas_html:
  html=html.replace(" NOADAPTAR. ",etiqueta,1)


print("resultado final", html)