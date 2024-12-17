import json # Json file generated by ChatGPT
import pygame

# Open pieces.json with pieces informations
with open("pieces.json") as f:
    pieces = json.load(f)

# Initialize Pygame
pygame.init()

# Layout settings
screen_width = 700
square_size = screen_width // 8
primary_square_color = "#d5c9bb"
secondary_square_color = "#b2a696"

screen = pygame.display.set_mode((screen_width, screen_width))
 
current_player = "White" # white start
running = True
dragging_piece = None  # Currently dragged piece
# Dictionaries for images and starting positions

pieces_color = {}
pieces_positions = {}
pieces_images =  {} 

for piece in pieces["pieces"]:
        piece_id = piece["id"] # un ID différent pour chaque pièce pour eviter de reécrire par dessus
        pieces_color[piece_id] = piece["color"]
        pieces_positions[piece_id] = piece["position"] # prend la position de chaque pièce
        image = pygame.image.load(piece["image"]) # prend l'image de chaque pièce
        pieces_images[piece_id] = pygame.transform.scale(image, (square_size, square_size)) # redimensionne l'image


# Draw a chess grid by coloring every other square. 
def draw_chessboard():
    for row in range(8):
        for col in range(8):
            # Determines the color of the square
            color = pygame.Color(primary_square_color) if (row + col) % 2 == 0 else pygame.Color(secondary_square_color)
            # Draw the square
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

# Draw a piece by taking the piece image and initial cordonates

def draw_piece(piece_name, x, y):
    image = pieces_images[piece_name]
    pos_x = (x * square_size) + (square_size - image.get_width()) // 2
    pos_y = (y * square_size) + (square_size - image.get_height()) // 2
    rect = pygame.Rect(pos_x, pos_y, image.get_width(), image.get_height())
    screen.blit(image, (pos_x, pos_y))
    return rect

#def draw():
    # faire une fonction pour toutes les draw possibles


#################################################################
# faire une fonction  pour chaque mouvement pour simlifier le code et faire les échecs (et mat)
#################################################################

def promote_piece(piece_id, piece_color):
    print(f"Promoting {piece_id} as {piece_color}")#test
    
    
    if piece_color == "White":
        options = ["w_queen", "w_bishop", "w_rook", "w_knight"] 
    elif piece_color == "Black":
        options = ["b_queen", "b_bishop", "b_rook", "b_knight"]
        print(options)# test
    
    choice = None

    # afficher le soptions de promotions
    running = True
    while running is True:
        for event in pygame.event.get(): # parcourt tous les éléments générés par pygame
            if event.type == pygame.QUIT: # vérifie si l'utilisateur a cliqué pour fermer la fenetre
                pygame.quit()
                exit()
            
            # gestion des clics
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # vérifie si un clic gauche a été fait.
                mouse_x, mouse_y = pygame.mouse.get_pos() # Get x, y cordonates of the mouse
                for i, option in enumerate(options): # Parcourt les options de promotion pour dessiner leurs boutons.
                    button_rect = pygame.Rect(20 + i * 170, 300, 150, 100 ) # position x, positon y, taille
                    if button_rect.collidepoint(mouse_x, mouse_y):
                        choice = option # enregistre le choix 
                        running = False # sortir de la boucle après un choix

        screen.fill("#000000") # remplit l'ecran de noir

        # Afficher le message
        font = pygame.font.Font(None, 36) # crée une police d'ecriture de 36
        message = font.render("choisissez une pièce", True,  pygame.Color("#FFFFFF")) # affiche le message en blanc #True rend le texte plus lisse
        screen.blit(message, (150, 200)) # position du message

        for i, option in enumerate(options):
            button_rect = pygame.Rect(20 + i * 170, 300, 150, 100)
            pygame.draw.rect(screen, pygame.Color("#808080"), button_rect) # dessine un carré gris

            # affiche le texte de chaque bouton
            option_text = font.render(option, True, pygame.Color("#000000")) #True rend le text plus lisse
            text_rect = option_text.get_rect(center=button_rect.center) # place le texte au centre du bouton
            screen.blit(option_text, text_rect) #place le message au dessus

        pygame.display.flip()


    # mettre à jours l'image et le type de la pièce prommue
    for piece in pieces["pieces"]:
        if piece["id"] == piece_id:
            piece["type"] = f"{choice}"
            new_image = f"./pieces/{choice}_png_shadow_512px.png"
            print(new_image) # test
            image = pygame.image.load(new_image)
            pieces_images[piece_id] = pygame.transform.scale(image, (square_size, square_size))
            break

    draw_chessboard() #reaffiche l'echiqier

    for piece_name, (piece_x, piece_y) in pieces_positions.items():
        draw_piece(piece_name, piece_x, piece_y) # redessine chaque pièce à sa position

    pygame.display.flip() # reaffiche les changement à l'ecran


        
def check_promotion(piece_type, piece_position, piece_id):
    if piece_type == "White_Pawn" and piece_position[1] == 7:
        promote_piece(piece_id, "White")
    elif piece_type == "Black_Pawn" and piece_position[1] == 0:
        promote_piece(piece_id, "Black")


def move_piece(piece_id, new_position): # déplace une pièce et capture une autre si necessaire
    global pieces_positions #Accède à la variable globale pieces_positions qui contient les positions actuelles de toutes les pièces
    
    for target_id, target_pos in pieces_positions.items(): # parcourt toutes les pièces du jeu
        current_color = next(piece["color"] for piece in pieces["pieces"] if piece["id"] == dragging_piece)
        target_color = next(piece["color"] for piece in pieces["pieces"] if piece["id"] == target_id)
        if target_pos == new_position and target_id != piece_id and current_color != target_color: #si la position de la cible est la même que la nouvelle position de la pièce jouée et qu'elles ne sont pas les mêmes  
            del pieces_positions[target_id] # capture
            break # arrête la bouvle dès qu'une pièce est mangée

    pieces_positions[piece_id] = new_position # met à jour la position

def handle_drag_and_drop():
    global dragging_piece, piece_id, pieces_color, current_player, can_catch
    # Prevents from crashing
    move_made = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        # Detect mouse button down to start dragging
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check if left button is pressed
            mouse_x, mouse_y = pygame.mouse.get_pos() # Get x, y cordonates of the mouse
            for piece_id, (piece_x, piece_y) in pieces_positions.items(): # Get x, y cordonates and id of the pieces
                piece_rect = draw_piece(piece_id, piece_x, piece_y) # Draw the piece 

                if piece_rect.collidepoint(mouse_x, mouse_y): # Verify if the piece collide with the mouse 
                    dragging_piece = piece_id # Set the piece as beeing dragged
                    break

        # Detect mouse button up to drop the piece
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1: # Check if left butter has been unpressed
            if dragging_piece: # Check if a piece if beeing dragged
                mouse_x, mouse_y = pygame.mouse.get_pos() # Get x, y cordonates of the mouse 
                new_x, new_y = mouse_x // square_size, mouse_y // square_size  # Snap the piece to the nearest square
                if 0 <= new_x < 8 and 0 <= new_y < 8: # Chessboard limit
                    
                    actual_position = pieces_positions[dragging_piece]

                    piece_settings = next(piece for piece in pieces["pieces"] if piece["id"] == dragging_piece)
                    piece_owner = next(piece["color"] for piece in pieces["pieces"] if piece["id"] == dragging_piece)
                    
                    piece_type = piece_settings["type"]
                    initial_position = piece_settings["position"]

                    is_allowed = False
                    if piece_type == "Black_Pawn":
                        allowed_x_moves = [0]
                        allowed_x_catching_moves = [-1, 1]
                        allowed_y_catching_moves = [1]

                        if actual_position == initial_position:
                            allowed_y_moves = [1, 2]
                        else:
                            allowed_y_moves = [1]

                        # Vérifie si une capture est possible
                        for target_id, target_position in pieces_positions.items():
                            if [new_x, new_y] == target_position and actual_position[0] - new_x in allowed_x_catching_moves and actual_position[1] - new_y in allowed_y_catching_moves:
                                is_allowed = pieces_color[target_id] != piece_owner
                                break

                        # Vérifie si le mouvement est en ligne droite sans capture
                        if (actual_position[0] - new_x in allowed_x_moves) and (actual_position[1] - new_y in allowed_y_moves):
                            if not any([new_x, new_y] == position for position in pieces_positions.values()):  # Case libre
                                is_allowed = True

                    elif piece_type == "White_Pawn":
                        allowed_x_moves = [0]
                        allowed_x_catching_moves = [-1, 1]
                        allowed_y_catching_moves = [-1]

                        if actual_position == initial_position:
                            allowed_y_moves = [-1, -2]
                        else:
                            allowed_y_moves = [-1]

                        # Vérifie si une capture est possible
                        for target_id, target_position in pieces_positions.items():
                            if [new_x, new_y] == target_position and actual_position[0] - new_x in allowed_x_catching_moves and actual_position[1] - new_y in allowed_y_catching_moves:
                                is_allowed = pieces_color[target_id] != piece_owner
                                break

                        # Vérifie si le mouvement est en ligne droite sans capture
                        if (actual_position[0] - new_x in allowed_x_moves) and (actual_position[1] - new_y in allowed_y_moves):
                            if not any([new_x, new_y] == position for position in pieces_positions.values()):  # Case libre
                                is_allowed = True

                    
                    elif piece_type == "w_knight" or piece_type == "b_knight":
                        if (abs(actual_position[0] - new_x) == 2 and abs(actual_position[1] - new_y) == 1) or (abs(actual_position[0] - new_x) == 1 and abs(actual_position[1] - new_y) == 2):
                            is_allowed = True

                    elif piece_type == "w_bishop" or piece_type == "b_bishop": 
                        if abs(actual_position[0] - new_x) == abs(actual_position[1] - new_y):
                            is_allowed = True    

                    elif piece_type == "w_rook" or piece_type == "b_rook":
                        allowed_y_moves = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7,]
                        allowed_x_moves = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7,]

                        if ((actual_position[0] - new_x in allowed_x_moves) and (actual_position[1] - new_y == 0)) or ((actual_position[0] - new_x == 0) and (actual_position[1] - new_y in allowed_y_moves)):
                            is_allowed = True

                    
                    elif piece_type == "w_queen" or piece_type == "b_queen":
                        allowed_y_moves = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7,]
                        allowed_x_moves = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7,]

                        if (((actual_position[0] - new_x in allowed_x_moves) and (actual_position[1] - new_y == 0)) or ((actual_position[0] - new_x == 0) and (actual_position[1] - new_y in allowed_y_moves))) or abs(actual_position[0] - new_x) == abs(actual_position[1] - new_y):
                            is_allowed = True

                    elif piece_type == "King":
                        allowed_x_moves = [-1, 0, 1]
                        allowed_y_moves = [-1, 0, 1]
                        
                        if (actual_position[0] - new_x in allowed_x_moves) and (actual_position[1] - new_y in allowed_y_moves):
                            is_allowed = True

                    if piece_owner != current_player:
                        is_allowed = False # Prevents from playing to times 

                    for position in pieces_positions:
                        if [new_x, new_y] == pieces_positions[position] and piece_owner == pieces_color[position]:
                            is_allowed = False # Prevents from catching self color
                   
                    if is_allowed:
                        pieces_positions[dragging_piece] = [new_x, new_y]
                        move_piece(dragging_piece, [new_x, new_y])
                        check_promotion(piece_type, pieces_positions[dragging_piece], dragging_piece)
                        dragging_piece = None
                        move_made = True
                           
                    
                    else:
                        dragging_piece = None 
                        print("Movement in not allowed")

                    
                    if move_made:
                        current_player = "Black" if current_player == "White" else "White"   
                             
                
                else:
                    print("Invalid movement") 

    return True

# Main loop
while running:
    running = handle_drag_and_drop()

    # Draw chessboard
    draw_chessboard()

    # Draw all pieces
    for piece_name, (piece_x, piece_y) in pieces_positions.items():
        if piece_name == dragging_piece:
            # If dragging, move the piece with the mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pos_x = mouse_x - (square_size // 2)
            pos_y = mouse_y - (square_size // 2)
            screen.blit(pieces_images[piece_name], (pos_x, pos_y))
        else:
            draw_piece(piece_name, piece_x, piece_y)

    pygame.display.flip()

# Quit Pygame
pygame.quit()


