#SYSTEME DE RECONNAISSANCE PAR SILHOUETTE
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from numpy.lib.type_check import imag
import os
import streamlit as st
from PIL import Image
import imagehash
import io
import json
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
from datetime import time
minimum = 4000 

frame1 = None

cap = cv2.VideoCapture(2)    

jina=""

path = 'images_saved'
calc=0
trouve="non"
personne=""
etat=""
detection="aucune"
mode='MODE DETECTION'
taille_mot=""
detail=""
# Les methodes d'extraction de Arrière-plan
mog = cv2.createBackgroundSubtractorMOG2()
mog.setShadowValue(0)
knn = cv2.createBackgroundSubtractorKNN()
knn.setShadowValue(0)
count = 0
i=0
#le style CSS pour notre page web
st.markdown(
    
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 350px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 350px;
        margin-left: -350px;
    }

    

    </style>
    """,
    unsafe_allow_html=True,
)
execution=""
st.sidebar.title("LES OPTIONS")
start=st.sidebar.button("STOPPER")
run=st.sidebar.checkbox("Lancer la camera")
#les differents mode de selection
app_mode = st.sidebar.selectbox('Selectionner le mode',
['Accueil','Détection','Enregistrement','Calibrage'])

method = st.sidebar.selectbox('Selectionner la methode',
['KNN','ABS','MOG2'])

if app_mode =='Accueil':
    st.markdown('Accueil')
    st.title("RECONNAISSANCE PAR SILHOUETTE")
    enregistrement="non"
    image = Image.open('silouette.jpg')
    st.image(image, caption='Identification par silhouette')
if app_mode =='Détection':
    st.title("LA DETECTION")
    
   
    claire=st.image([])
    enregistrement="non"
if app_mode =='Calibrage':
    st.title("CALIBRAGE") 
    silo=st.image([])
    enregistrement="non"

if app_mode =='Enregistrement':
    st.title("ENREGISTREMENT")
    vider=st.button("VIDER LES DONNEES")
    etat = st.selectbox('La position',
    ['Entree','Sortie'])
    jina=st.text_input("Entrer le nom","")
    enregistrement="oui"
    st.write(jina)
    silo=st.image([])
    #la partie pour vider les donnees de la base de donnees
    if vider:
       with open("data.json", "w") as file:
           file.write("") 
       for fito in os.listdir("DataBase/") :
           os.remove("DataBase/" + "/" + fito)
#la lecture de la frame du camera     
while run:
    ret, frame = cap.read()
  
    frame=cv2.blur(frame, (3, 3))
    vid = cv2.flip(frame,1)
    
    if method == 'MOG2':
        bgs = mog.apply(vid)
       
        
    elif method == 'KNN':
        bgs = knn.apply(vid)
        
    
    elif method == 'ABS':
        frame = cv2.GaussianBlur(vid,(7,7),0)
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        
        if frame1 is None:
            frame1 = frame
            continue 
        
        framedelta = cv2.absdiff(frame1,frame)
        retval, bgs = cv2.threshold(framedelta.copy(), 50, 255, cv2.THRESH_BINARY)
    
    mask = np.zeros_like(frame)

    if enregistrement=="oui":
       
        mode=""
   
    contours,_ = cv2.findContours(bgs, mode= cv2.RETR_TREE, method= cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours,key=cv2.contourArea,reverse= True)
    cv2.putText(vid,"Systeme de detection",(20,20),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(0,255,0,2))
    cv2.putText(vid,personne,(400,50),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,0,0,2))
    

    
    for cnt in contours:
        if cv2.contourArea(cnt) < minimum:
                continue 

        
        (x,y,w,h) = cv2.boundingRect(cnt)
        cv2.rectangle(vid,(x,y),(x+w,y+h),(0,255,10),1)
       
        #cv2.putText(vid,etat,(1000,20),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(0,0,255,2))
        cv2.putText(vid,mode,(20,50),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(0,0,255,2))
        calc=calc+1
        
       #on patiente unpeu avant de commencer a appliquer les differentes techniques sur la frame
        if calc>5:
            calc=0
            #cv2.putText(vid,personne,(200,60),cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(255,0,0,2))
            if app_mode =='Détection':
                       detection=personne
                       st.header(detection)
            #la partie de sauvegarde
            frame = imagehash.whash(Image.fromarray(bgs))

            if enregistrement=="oui":

                cv2.imwrite("DataBase/"+jina+"_"+etat+"_%d.jpg" % count, bgs)
                
                b=".jpg"
                nom=jina+str(i)
                nom=nom+"_"+etat
                fra=str(frame)
                donnees = {nom:fra}
                i += 1
                contenu=os.path.getsize("data.json")
                if contenu==0:
                    with io.open('data.json', 'w', encoding='utf8') as outfile:
                          str_ = json.dumps(donnees,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
                          outfile.write(to_unicode(str_))
                if contenu!=0:
                    file=open('data.json', 'r')
                    fichier= json.load(file)
                    fichier.update(donnees)
                    with io.open('data.json', 'w', encoding='utf8') as outfile:
                          str_ = json.dumps(fichier,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
                          outfile.write(to_unicode(str_))
                count += 1
            #la partie de reconnaissance de la personne
            if enregistrement=="non":
                #on charge les donnees se trouvant dans notre dictionnaire
                conte=os.path.getsize("data.json")
                
                with open('data.json') as data_file:
                     data_loaded = json.load(data_file)
               
                for key in data_loaded:
                   
                   recover_silhou = imagehash.hex_to_hash(data_loaded[key])
                   silhou_personne=recover_silhou-frame
                   print(silhou_personne)
                   #si la valeur est dans cette intervalle donc la personne est trouvee
                   if silhou_personne<=1:
                      
                      personne=key
                      taille_mot=len(personne)
                      #on supprime les chiffre se trouvant dans la variable persone
                      personne = ''.join([i for i in personne if not i.isdigit()])
                     
                      detection=personne
                      

            cv2.drawContours(mask,cnt,-1,255,3)

            break

    #cv2.imshow('frame',vid)
    #cv2.imshow('BGS',bgs)
    if app_mode =='Détection':
       vid = cv2.cvtColor(vid,cv2.COLOR_BGR2RGB)

       claire.image(vid)
       #st.sidebar.title(personne)
    if app_mode =='Enregistrement':
       silo.image(bgs)
    if app_mode =='Calibrage':
       silo.image(bgs)   
    if start:
        break

  
cap.release()
cv2.destroyAllWindows()
