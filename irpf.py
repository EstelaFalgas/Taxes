

class Usuario:
    def __init__(self, bruto: float, tributación_conjunta: bool, numero_de_hijos: int, menores_de_3_años: int):
        self.bruto= bruto
        self.tributación_conjunta= tributación_conjunta                                 #Factores a reducir la base imponible                                                                              
        self.hijos= numero_de_hijos                                                     #Bruto, Numero de hijos, Menores de 3 años, Tributación conjunta
        self.menores_3= menores_de_3_años                                              
        self.base_imponible= self.bruto*0.9365                                          # Seguridad Social
        self.irpf= self.IRPF(self)
        if self.tributación_conjunta:                                                   # Tributación Conjunta
            self.base_imponible-=3400
        
        if self.hijos>4:                                                                # Reducción por hijos
            new= self.irpf.ded_por_hijo
            for x in range(len(self.hijos-4)):
                new.append(4500)
            for y in new:
                self.base_imponible-= y
        elif self.hijos>0:                                                              # Reducción por hijos menores de 3 años
            for z in self.irpf.ded_por_hijo[:self.hijos]:
                self.base_imponible-= z
        self.base_imponible-= 2800*self.menores_3

        self.neto= self.irpf.bruto_neto_impuestos_mensualidad()["neto"]                 # Salario neto , Impuestos pagados , Mensualidad
        self.impuestos= self.irpf.bruto_neto_impuestos_mensualidad()["impuestos"]
        self.mensualidad= self.irpf.bruto_neto_impuestos_mensualidad()["mensualidad"]

    class IRPF:
        def __init__(self, Usuario):
            self.usuario= Usuario
            self.tipo_estatal= [9.5,12,15,18.5,22.5,24.5]
            self.tipo_autonómico= [8.5,10.7,12.8,17.4,20.5, 20.5]
            self.pocentages = [self.tipo_estatal[i] + self.tipo_autonómico[i] for i in range(len(self.tipo_estatal))]
            self.tramos_dict = {(0, 12450): self.pocentages[0], (12450, 20200): self.pocentages[1], (20200, 35200): self.pocentages[2], 
                                (35200, 60000): self.pocentages[3], (60000, 300000): self.pocentages[4], (300000, 1000000): self.pocentages[5]}
            self.porcentage_SSocial = 6.35
            self.tramos_salarios = [i[1] for i in list(self.tramos_dict.keys())[0:-1]]
            self.tramos_porcentages = [i for i in list(self.tramos_dict.values())] 
            self.ded_por_hijo= [2400, 2700, 4000, 4500]
            self.tramos_a_reducir= self.calcular_tramos_a_reducir()

        def calcular_tramos_a_reducir(self):
            tramos=  [12450, 7750, 15000, 24800, 240000]
            tramos_a_reducir= []                                                                        #tramos_a_reducir: suman a la base imponible
            base= tramos[0]
            if self.usuario.base_imponible < base: #si menos de 12450 (primer tramo)
                tramos_a_reducir.append(self.usuario.base_imponible)
                return tramos_a_reducir
            else:   
                tramos_a_reducir.append(tramos[0]) #si mas de 12450, ir sumando a la base hasta que iguale a la base imponible.
                for i in range(1,len(tramos)):
                    if self.usuario.base_imponible> sum([base,tramos[i]]):
                        base+= tramos[i]
                        tramos_a_reducir.append(tramos[i])
                    else:
                        tramos_a_reducir.append(self.usuario.base_imponible - base)
                        return tramos_a_reducir
                
                return tramos_a_reducir

                
        def deducción(self):
            a_reducir = self.calcular_tramos_a_reducir()                                                       # Impuestos (reducido del bruto)
            return sum([a_reducir[i] * self.tramos_porcentages[i] / 100 for i in range(len(a_reducir))])
        
        def bruto_neto_impuestos_mensualidad(self):                                                            # Cálculo del neto y mensualidad
            neto = self.usuario.bruto - self.deducción() 
            return {"bruto": self.usuario.bruto, 
                    "neto": "{:.2f}".format(round(neto, 2)), 
                    "impuestos": "{:.2f}".format(round(self.usuario.bruto-neto,2)), 
                    "mensualidad": "{:.2f}".format(round(neto/12, 2))}