> I file usati e modificati in data 22/02/23 sono stati messi in "temp" nel caso qualcuno volesse già dargli un'occhiata. 
> Verranno riorganizzati nei giorni a seguire.

## Anon-Comb

> Sono già nei piani dei cambi/aggiustamenti da fare, ad esempio l'ordine di inserimento dei livelli nelle tuple e l'aggiunta di una variabile che terrà a parte la tabella originaria, cose alle quali non ci avevo fatto caso prima.
> Quindi se si vedono delle parti di codice che restituiscono o fanno qualcosa di diverso da quello descritto quì è perchè mi sono accorto di tali errori solo durante la stesura di questo README.
> Provvederò a fare i cambi necessari nei giorni a venire, ma nel mentre metto a disposizione questo file per dare del tempo di capire cosa ho scritto e come l'ho implementato.

Visto che si andrà a riutilizzare la maggior parte del codice del laboratorio presente su Aula Web ho optato per riutilizzare parte di tale codice e modificarlo a seconda delle esigenze di Incognito.

Partendo dal metodo `anonymize`, tra gli attributi inizializzati ho aggiunto semplicemente `qi_frequency_candidates`, il quale sarà una lista di Dizionari e avrà il compito di salvare tutte le istanze della tabella generalizzata (salvata sotto forma di dizionario) mentre viene generalizzata combinazione dopo combinazione.
Il resto delle variabili inizializzate, compresi `qi_frequency` e `domains`, sono rimasti invariati.

### Generalization
A questo punto viene creata una lista di combinazioni (tuple) tramite il metodo `combination()`, queste saranno le combinazioni che verranno usate per generalizzare la tabella.
```python
combinations = combination(qi_names,dghs)
```
Le tuple in se specificheranno solo il livello di generalizzazione che ogni attributo dovrà seguire per ogni combinazione, ma avendo inserito i livelli ordinatamente basterà iterare i valori della tupla ed eseguire le generalizzazioni in modo ordinato per andare in confusione.

Al posto di un `while True`, dal quale si dovrà poi uscire con un break, ho usato gli elementi in `combinations` come criterio per chiudere il ciclo For. _(una volta lette tutte le tuple `data` esco dal For)_

Qui al posto di usare `attribute_idx` per decidere che attributo generalizzare userò la tupla `data`, la quale contiene in ordine che livello di generalizzazione ogni QI deve avere.

Il processo di generalizazione (in locale) è rimasto quasi invariato, ho aggiunto giusto un _For_ per eseguire tale procedimento su tutti gli attributi necessari, e reso `generalized_value` un dizionario, per poter lavorare allo stesso modo nei multipli cicli di generalizzazione.

```python
new_qi_sequence = list(qi_sequence)
for id, gen_val in generalized_value.items():
    new_qi_sequence[id] = gen_val
new_qi_sequence = tuple(new_qi_sequence)
```
Poi si passa a salvare i valori generalizzati nei corrispettivi campi, appartenenti alla tupla presa in esame. (passaggio Tupla -> Lista -> Tupla necessario per poter modificare i valori, visto che i valori nelle tuple non si sono modificabili)

Gli aggiornamenti di `qi_frequency` e `domains` sono rimasti prevalentemente invariati.

```python
qi_frequency_candidates.append(qi_frequency)
```
E aggiungo lo stato della tabella attuale alla lista dei candidati `qi_frequency_candidates`.

### K-Anon Minimum
> Ancora da implementare

### Output file
Questa parte ha subito pressochè zero cambiamenti.
Tra le sequenze di attributi salvati, vengono tolti (o "soppressi") solo quelli che hanno una ripetizione inferiore a K
```python
if data[0] < k:
    qi_frequency.pop(qi_sequence)
```
E in fine si inizia a scrivere la tabella generalizzata nel file di output (formattando la riga da scrivere con `_set_values`).

## Combinations
Questi metodi si possono scrivere tranquillamente nello stesso file di `anonymize`, ma richiederanno l'implementazione di un metodo `tree.length` per poter funzionare.

`combination` farà una breve preparazione per iniziare a lanciare ricorsivamente `recursiveComb`, dandogli la lunghezza della ricorsione `rec_length` (che servirà da indice per specificare il massimo livello di generalizazione che ciascun attributo avrà), i nomi dei vari attributi (`qi_names`), i vari alberi di generalizzazione (`dghs`) e la lista `comb` che conterrà tutte le combinazioni.

`recursiveComb` (se `rec_length` è diverso da zero) entrerà in un ciclo di ricorsione che si ripeterà tante volte quanto siano i livelli di generalizzazione dell'attributo preso in esame nella ricorsione corrente (che come specificato precedentemente verrà specificato da `rec_length`).
```python
for i in range(dghs.length(qi_names[rec_length])):
    recursiveComb(rec_length - 1, qi_names, dghs, comb, base+(i,))
```
Alla chiamata ricorsiva si daranno in input le stesse variabili specificate prima, con un paio di modifiche:
`rec_length` verrà ridotto di 1 e in aggiunta si darà una tupla contenente i livelli di generalizzazione delle ricorsioni precedenti (`base`) concatenata con la tupla composta dal livello di generalizzazione dell'attributo preso in esame nella ricorsione corrente (`(i,)`).
_P.S.: Questo non conta come "modificare" una tupla, si manda semplicemente una tupla composta da due tuple concatenate._
```python
for i in range(dghs.length(qi_names[rec_length])):
    comb.append(base + (i,))
```
Arrivati all'ultimo attributo dei QI (`rec_length == 0`) si entrerà in un altro ciclo _For_ che inizierà a inserire in `comb` varie concatenazioni, incrementando di 1 il livello di generalizzazione dell'ultimo attributo per ogni inserimento (`append`).
Una volta uscito dal ciclo _For_ si tornerà alla ricorsione precedente, la quale incrementerà il suo livello di generalizzazione e chiamerà nuovamente (ricorsivamente) la funzione sul seguente attributo.
