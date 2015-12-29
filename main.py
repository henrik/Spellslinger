#!/usr/bin/env python
import random
import time
import copy
from termcolor import colored 

class Character(object):

    def __init__(self, name = "noname", hp = 100, mp = 0, armor = 0, attack = 0, 
                 abilities = [], ptype = "NPC", effects = {}): 

        self.name = name         
        self.hp = hp
        self.mp = mp
        self.armor  = armor
        self.attack = attack
        self.abilities = abilities
        self.effects = effects
        self.ptype = ptype
        self.moves = []
        self.mana_spent = 0
        self.mpmax = mp
        self.hpmax = hp

class Battle(object):

    def __init__(self, attacker, defender, difficulty = "Normal", slow_text = True):

        self.attacker = attacker
        self.defender = defender
        self.turn = "a"
        self.nturn = 0
        self.status = True
        self.outcome = "No outcome"
        self.slow_text = slow_text
        self.difficulty = difficulty
        
        if slow_text:
            print colored("\n... WELCOME TO THE BATTLE...", "yellow")
            wait_long()
            print colored("... %s vs. %s ..." % (attacker.name, defender.name), "yellow")
            wait()

            print colored("\n... %s stats: ..." % attacker.name, "blue")
            wait()
            print colored("... HP: %s..." % attacker.hp, "blue")
            wait()
            print colored("... MP: %s..." % attacker.mp, "blue")
            wait()
            print colored("... Armor: %s..." % attacker.armor, "blue")
            wait()
            print colored("... Attack: %s..." % attacker.attack, "blue")
            wait()
            print colored("... Abilities: %s..." % attacker.abilities, "blue")

            wait_long()

            print colored("\n... %s stats: ..." % defender.name, "red")
            wait()
            print colored("... HP: %s..." % defender.hp, "red")
            wait()
            print colored("... MP: %s..." % defender.mp, "red")
            wait()
            print colored("... Armor: %s..." % defender.armor, "red")
            wait()
            print colored("... Attack: %s..." % defender.attack, "red")
            wait()
            print colored("... Abilities: %s...\n" % defender.abilities, "red")
            wait()


    def make_turn(self):
        self.nturn += 1
        #print "\n...Starting turn number: %s...\n" % self.nturn
        
        if self.slow_text:
            wait()

        if self.difficulty == "Hard":
            if self.turn == "a":
                self.attacker.hp -= 1
        
        # Check status
        self.check_health()
        if not self.status:
            return self

        # Evaluate effects happening in beginning of turn
        self.eval_effects_start()

        # Check status
        self.check_health()
        if not self.status:
            return self

        # check mana
        self.check_mana()
        if not self.status:
            return self 
        
        if self.slow_text:
            message = colored("Status:\n", "yellow")
            
            # Healthbars
            hp_prc_a = float(self.attacker.hp) / float(self.attacker.hpmax)
            hp_prc_d = float(self.defender.hp) / float(self.defender.hpmax)
            hp_blocks_a = int(40.0 * hp_prc_a)
            hp_blocks_d = int(40.0 * hp_prc_d)
            
            # Manabar
            mp_prc_a = float(self.attacker.mp) / float(self.attacker.mpmax)
            mp_prc_d = float(self.defender.mp) / float(self.defender.mpmax)
            mp_blocks_a = int(40.0 * mp_prc_a)
            mp_blocks_d = int(40.0 * mp_prc_d)

            a_message = ""

            for i in xrange(hp_blocks_a):
                a_message += colored("#", "red")
            
            a_message += "\n"
            
            for i in xrange(mp_blocks_a):
                a_message += colored("#", "blue")
            
            a_message += colored("\n%s has %s HP, %s MP, " % 
                         (self.attacker.name, self.attacker.hp, self.attacker.mp),
                         "yellow")
            
            for effect in self.attacker.effects:
                a_message += colored("%s is active (%s turn remaining), " % 
                             (effect, self.attacker.effects[effect]), "yellow") 
            
            a_message += "\n"

            d_message = ""
            
            for i in xrange(hp_blocks_d):
                d_message += colored("#", "red")
            
            d_message += "\n"
            
            for i in xrange(mp_blocks_d):
                d_message += colored("#", "blue")
            
            d_message += colored("\n%s has %s HP, %s MP, " % 
                                 (self.defender.name, 
                                 self.defender.hp, 
                                 self.defender.mp), "yellow")

            for effect in self.defender.effects:
                d_message += colored("%s is active (%s turn remaining), " % 
                                     (effect, 
                                      self.defender.effects[effect]), "yellow") 
            d_message += "\n"

            if self.attacker.name == "wizard":
                print message + a_message + d_message
            elif self.defender.name == "wizard":
                print message + d_message + a_message
            else:
                print message + a_message + d_message
        
        if self.slow_text:
            wait()

        # Decide on ability
        ability = self.choose_ability()

        # Perform action
        getattr(self, ability)()
        
        self.attacker.moves.append(ability)

        if self.slow_text:
            wait()

        # Check status
        self.check_health()
        if not self.status:
            return self

        # Evaluate effects expiring at the end of turn
        self.eval_effects_end()

        # End turn
        self.end_turn()

        return self

    def choose_ability(self):

        ability_names = {"Attack" : "attack",
                         "Magic Missile" : "magic_missile",
                         "Drain" : "drain",
                         "Shield" : "shield",
                         "Poison" : "poison",
                         "Recharge" : "recharge"}
        
        mana_cost = {"Attack" : 0,
                     "Magic Missile" : 53,
                     "Drain" : 73,
                     "Shield" : 113,
                     "Poison" : 173,
                     "Recharge" : 229}

        description = {"Attack" : "Normal physical attack",
                       "Magic Missile" : "Magic Missile costs 53 mana. It"+ 
                                         "instantly does 4 damage",
                       "Drain" : "Drain costs 73 mana. It instantly does 2"+ 
                                 " damage and heals you for 2 hit points.",
                       "Shield" : "Shield costs 113 mana. It starts an effect"+
                                  " that lasts for 6 turns. While it is active"+
                                  ", your armor is increased by 7.",
                       "Poison" : "Poison costs 173 mana. It starts an effect"+
                                  " that lasts for 6 turns. At the start of "+
                                  "each turn while it is active, it deals the"+
                                  " boss 3 damage.",
                       "Recharge" : "Recharge costs 229 mana. It starts an "+
                                    "effect that lasts for 5 turns. At the"+
                                    " start of each turn while it is active,"+
                                    " it gives you 101 new mana."}

        # See what abilities are avaiable
        message = "Choose ability:\n"
        
        avail = self.avail_abilities()

        abilities = {}
        for i, abi in enumerate(avail):
            abilities[str(i+1)] = abi
            message += "%s : %s (%s)\n" % (i+1, abi, description[abi])
            
        if self.attacker.ptype == "Player":
            ability_name = abilities[str(input(colored(message, "yellow")))]
        if self.attacker.ptype == "NPC":
            ability_name = random.choice(avail)

        ability = ability_names[ability_name]

        return ability

    def avail_abilities(self):

        mp = self.attacker.mp 
        avail = []
        for ability in self.attacker.abilities:
            
            if ability == "Magic Missile" and mp >= 53:
                avail.append(ability)
            
            if ability == "Drain" and mp >= 73:
                avail.append(ability)
            
            if ability == "Shield" and \
            mp >= 113 and \
            "Shield" not in self.attacker.effects.keys():
                avail.append(ability)
            
            if ability == "Poison" and \
            mp >= 173 and \
            "Poison" not in self.defender.effects.keys():
                avail.append(ability)
            
            if ability == "Recharge" and \
            mp >= 229 \
            and "Recharge" not in self.attacker.effects.keys():
                avail.append(ability)
            
            if ability == "Attack":
                avail.append(ability)

        return avail

    def check_mana(self):
        if self.attacker.mp < 53 and "Attack" not in self.attacker.abilities:
            self.status = False
            self.outcome = colored("%s is out of options (no mana?)" % 
                                   self.attacker.name, "yellow")
        return self

    def check_health(self):

        if self.attacker.hp <= 0:
            self.status = False
            self.outcome = "%s had died, %s has won!" % (self.attacker.name, self.defender.name)
        
        if self.defender.hp <= 0:
            self.status = False
            self.outcome = "%s has died, %s has won!" % (self.defender.name, self.attacker.name)

        return self

    def eval_effects_start(self):
        ''' Evaluate effects happening at the beginning of the turn '''

        # ATTACKER
        if "Poison" in self.attacker.effects.keys():
            
            if self.slow_text:
                print colored("Poison does 3 damage to %s\n" % 
                              (self.attacker.name), "green")
                wait()
            self.attacker.hp -= 3
            
            if self.attacker.effects["Poison"] == 1:
                del self.attacker.effects["Poison"]
                print colored("Poison has worn off on %s\n" % 
                              (self.attacker.name), "green")
                wait()
            else:
                self.attacker.effects["Poison"] -= 1

        if "Recharge" in self.attacker.effects.keys():
            if self.slow_text:
                print colored("%s gains 101 mana through recharge\n" % 
                              (self.attacker.name), "blue")
                wait()
            self.attacker.mp += 101
            if self.attacker.effects["Recharge"] == 1:
                del self.attacker.effects["Recharge"]
                print colored("Recharge has worn off on %s\n" % 
                              (self.attacker.name), "blue")
                wait()
            else:
                self.attacker.effects["Recharge"] -= 1

        # DEFENDER
        if "Poison" in self.defender.effects.keys():
            if self.slow_text:
                print colored("Poison does 3 damage to %s\n" % 
                              (self.defender.name), "green")
                wait()
            self.defender.hp -= 3
            if self.defender.effects["Poison"] == 1:
                del self.defender.effects["Poison"]
                print colored("Poison has worn off on %s\n" % 
                              (self.defender.name), "green")
                wait()
            else:
                self.defender.effects["Poison"] -= 1

        if "Recharge" in self.defender.effects.keys():
            if self.slow_text:
                print colored("%s gains 101 mana through recharge\n" % 
                              (self.defender.name), "blue")
                wait()
            self.defender.mp += 101
            if self.defender.effects["Recharge"] == 1:
                del self.defender.effects["Recharge"]
                print colored("Recharge has worn off on %s\n" % 
                              (self.defender.name), "blue")
                wait()
            else:
                self.defender.effects["Recharge"] -= 1

        return self    

    def eval_effects_end(self):
        ''' Evaluate effects wearing off at the end of turn '''

        # Attacker
        if "Shield" in self.attacker.effects.keys():
            if self.attacker.effects["Shield"] == 1:
                del self.attacker.effects["Shield"]
                if self.slow_text:
                    print colored("Shield has worn off on %s\n" % 
                                  (self.attacker.name), "cyan")
                    wait()
                self.defender.armor -= 7
            else:
                self.attacker.effects["Shield"] -= 1
        
        # Defender
        if "Shield" in self.defender.effects.keys():
            if self.defender.effects["Shield"] == 1:
                del self.defender.effects["Shield"]
                if self.slow_text:
                    print colored("Shield has worn off on %s\n" % 
                                  (self.defender.name), "cyan")
                    wait()
                self.defender.armor -= 7
            else:
                self.defender.effects["Shield"] -= 1

        return self
        
    def attack(self):
        ''' Normal attack using physical force '''
        
        dmg = max(1, self.attacker.attack - self.defender.armor)
        if self.slow_text:
            message = colored("%s attacks %s for %s damage" % \
              (self.attacker.name, self.defender.name, dmg), "red")
            if "Shield" in self.defender.effects.keys(): 
                message += colored(" (%s blocked by Shield)" % 
                                   self.defender.armor, "cyan")
            message += "\n"
            print message
            wait()
        self.defender.hp -= dmg
        
        return self

    def magic_missile(self):
        ''' Attacker shoots magic missile at defender '''
        if self.slow_text:
            print colored("%s shoots magic missile at %s for 4 damage\n" % \
              (self.attacker.name, self.defender.name), "magenta")
            wait() 
        self.attacker.mp -= 53
        self.defender.hp -= 4
        self.attacker.mana_spent += 53

        return self

    def drain(self):
        ''' Attacker does damage to defender and heals himself '''
        if self.slow_text:
            print colored("%s drains 2 life from %s\n" % \
              (self.attacker.name, self.defender.name), "red") 
            wait()
        self.attacker.mp -= 73
        self.attacker.hp += 2
        self.defender.hp -= 2
        self.attacker.mana_spent += 73
        
        return self

    def shield(self):
        ''' Attacker applies "shield" for 6 turns '''
        if self.slow_text:
            print colored("%s activates shield for 6 turns\n" % 
                          self.attacker.name, "cyan") 
            wait()
        self.attacker.mp -= 113
        self.attacker.effects["Shield"] = 6
        self.attacker.armor += 7
        self.attacker.mana_spent += 113

        return self

    def poison(self):
        ''' Attacker applies poison to defender '''
        if self.slow_text:
            print colored("%s poisons %s for 6 turns\n" % \
                          (self.attacker.name, self.defender.name), "green") 
            wait()

        self.attacker.mp -= 173
        self.defender.effects["Poison"] = 6
        self.attacker.mana_spent += 173

        return self

    def recharge(self):
        ''' Attacker begins recharge effect '''
        if self.slow_text:
            print colored("%s activates recharge for 5 turns\n" % 
                          self.attacker.name, "blue") 
            wait()
        self.attacker.mp -= 229
        self.attacker.effects["Recharge"] = 5
        self.attacker.mana_spent += 229


        return self

    def end_turn(self):
        ''' End attackers turn, making defender the attacker '''

        if self.turn == "a":
            self.turn = "d"
        elif self.turn == "d":
            self.turn = "a"
   
        self.attacker, self.defender = self.defender, self.attacker
    
        return self

def wait():
    time.sleep(0.1)
    return

def wait_long():
    time.sleep(0.1)
    return

if __name__ == "__main__":
     
    wizard_abilities = ["Magic Missile", 
                        "Drain", 
                        "Shield", 
                        "Poison", 
                        "Recharge"]

    wizard = Character(name = "wizard",
                       hp = 50, 
                       mp = 500, 
                       armor = 0, 
                       attack = 0, 
                       abilities = wizard_abilities,
                       ptype = "Player",
                       effects = {})

    boss_abilities = ["Attack"]

    boss = Character(name = "boss",
                     hp = 71,
                     mp = 1,
                     armor = 0,
                     attack = 10,
                     abilities = boss_abilities,
                     effects = {})
   
    fight = Battle(copy.deepcopy(wizard), 
                   copy.deepcopy(boss))

    while fight.status:
        fight.make_turn()

    print colored(fight.outcome, "yellow")


