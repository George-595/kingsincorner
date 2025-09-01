"""
Kings in the Corner - Pure Streamlit Native Version
No HTML - only native Streamlit components for maximum compatibility
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import time
from game_manager import game_manager


# Page configuration
st.set_page_config(
    page_title="Kings in the Corner",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'player_id': None,
        'game_id': None,
        'player_name': "",
        'selected_cards': [],
        'show_rules': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def get_card_display(card):
    """Get card display text with color indicator."""
    if not card:
        return "🂠"
    
    rank = card['rank']
    suit = card['suit']
    color_indicator = "🔴" if card['color'] == 'red' else "⚫"
    
    return f"{color_indicator} {rank}{suit}"

def display_pile_simple(pile_data, pile_name, pile_type="foundation"):
    """Display a pile using only Streamlit components."""
    cards = pile_data.get('cards', [])
    is_empty = len(cards) == 0
    
    # Title
    if pile_type == "corner":
        st.subheader(f"👑 {pile_name.upper()}")
        st.caption("Corner Pile")
    else:
        st.subheader(f"📋 {pile_name.upper()}")
        st.caption("Foundation Pile")
    
    # Card display
    if is_empty:
        if pile_type == "corner":
            st.error("🚫 Kings Only")
        else:
            st.success("✅ Any Card")
        st.caption("Empty pile")
    else:
        # Show top card
        top_card = cards[-1]
        st.info(f"**{get_card_display(top_card)}**")
        
        # Show stack info
        if len(cards) > 1:
            st.caption(f"📚 {len(cards)} cards in stack")
            # Show recent cards
            recent = cards[-min(3, len(cards)):]
            recent_display = []
            for c in recent:
                recent_display.append(get_card_display(c))
            st.caption(f"Recent: {' → '.join(recent_display)}")
        else:
            st.caption("Single card")

def display_game_board(game_state):
    """Display the game board with clean layout."""
    st.markdown("## 🎲 Game Board")
    
    # Top row
    st.markdown("### Top Row")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_pile_simple(game_state['corner_piles']['nw'], "NW", "corner")
    
    with col2:
        display_pile_simple(game_state['foundation_piles']['north'], "North", "foundation")
    
    with col3:
        display_pile_simple(game_state['corner_piles']['ne'], "NE", "corner")
    
    # Middle row
    st.markdown("### Middle Row")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_pile_simple(game_state['foundation_piles']['west'], "West", "foundation")
    
    with col2:
        # Deck
        st.subheader("🃏 DRAW PILE")
        deck_size = game_state['deck_size']
        st.info(f"**{deck_size} cards remaining**")
        
        if st.button("🃏 Draw a Card", key="draw_card", type="primary", use_container_width=True):
            success, message = game_manager.draw_card(st.session_state.player_id)
            if success:
                st.success(message)
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(message)
    
    with col3:
        display_pile_simple(game_state['foundation_piles']['east'], "East", "foundation")
    
    # Bottom row
    st.markdown("### Bottom Row")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_pile_simple(game_state['corner_piles']['sw'], "SW", "corner")
    
    with col2:
        display_pile_simple(game_state['foundation_piles']['south'], "South", "foundation")
    
    with col3:
        display_pile_simple(game_state['corner_piles']['se'], "SE", "corner")

def display_hand_interface(player_data):
    """Display player hand with simple card selection."""
    if not player_data or not player_data['hand']:
        st.info("🃏 No cards in your hand")
        return
    
    st.markdown("## 🃏 Your Hand")
    st.write(f"You have {len(player_data['hand'])} cards. Click to select them:")
    
    # Display cards as simple buttons
    hand = player_data['hand']
    
    # Show cards in rows of 6
    cards_per_row = 6
    
    for i in range(0, len(hand), cards_per_row):
        cols = st.columns(cards_per_row)
        row_cards = hand[i:i+cards_per_row]
        
        for j, card in enumerate(row_cards):
            if j < len(cols):
                with cols[j]:
                    card_id = f"{card['rank']}{card['suit']}"
                    is_selected = card_id in st.session_state.selected_cards
                    
                    # Simple button with clear text
                    card_text = get_card_display(card)
                    button_text = f"{'✅ ' if is_selected else ''}{card_text}"
                    button_type = "primary" if is_selected else "secondary"
                    
                    if st.button(button_text, key=f"card_{i+j}", type=button_type, use_container_width=True):
                        if is_selected:
                            st.session_state.selected_cards.remove(card_id)
                        else:
                            st.session_state.selected_cards.append(card_id)
                        st.rerun()
    
    # Show selection summary
    if st.session_state.selected_cards:
        st.success(f"✅ Selected: {', '.join(st.session_state.selected_cards)}")
    else:
        st.info("👆 Click cards above to select them")

def display_actions_interface(game_state):
    """Display action interfaces."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Play Cards")
        
        if not st.session_state.selected_cards:
            st.warning("Select cards from your hand first!")
        else:
            # Pile selection
            all_piles = list(game_state['foundation_piles'].keys()) + list(game_state['corner_piles'].keys())
            
            target_pile = st.selectbox(
                "Choose destination:",
                all_piles,
                format_func=lambda x: f"{x.title()} ({'Corner' if x in game_state['corner_piles'] else 'Foundation'})",
                key="target_pile"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("🃏 Play Selected", key="play_cards", type="primary", use_container_width=True):
                    success_count = 0
                    failed_cards = []
                    
                    for card_id in st.session_state.selected_cards.copy():
                        rank = card_id[:-1]
                        suit = card_id[-1]
                        
                        success, message = game_manager.play_card(
                            st.session_state.player_id, rank, suit, target_pile
                        )
                        
                        if success:
                            success_count += 1
                            st.session_state.selected_cards.remove(card_id)
                        else:
                            failed_cards.append(f"{card_id}: {message}")
                            break
                    
                    if success_count > 0:
                        st.success(f"✅ Played {success_count} card(s)!")
                    
                    if failed_cards:
                        st.error(f"❌ {failed_cards[0]}")
                    
                    if success_count > 0:
                        time.sleep(0.5)
                        st.rerun()
            
            with col_b:
                if st.button("🧹 Clear Selection", key="clear_selection", use_container_width=True):
                    st.session_state.selected_cards = []
                    st.rerun()
    
    with col2:
        st.markdown("### 🔄 Move Piles")
        
        # Get moveable piles
        all_piles = list(game_state['foundation_piles'].keys()) + list(game_state['corner_piles'].keys())
        moveable_piles = []
        
        for pile_name in all_piles:
            if pile_name in game_state['foundation_piles']:
                pile = game_state['foundation_piles'][pile_name]
            else:
                pile = game_state['corner_piles'][pile_name]
            
            if pile['cards']:
                moveable_piles.append(pile_name)
        
        if not moveable_piles:
            st.info("No piles to move")
        else:
            from_pile = st.selectbox(
                "From pile:",
                moveable_piles,
                format_func=lambda x: f"{x.title()} ({'Corner' if x in game_state['corner_piles'] else 'Foundation'})",
                key="from_pile"
            )
            
            to_piles = [p for p in all_piles if p != from_pile]
            to_pile = st.selectbox(
                "To pile:",
                to_piles,
                format_func=lambda x: f"{x.title()} ({'Corner' if x in game_state['corner_piles'] else 'Foundation'})",
                key="to_pile"
            )
            
            if st.button("🔄 Move Pile", key="move_pile", type="primary", use_container_width=True):
                success, message = game_manager.move_pile(
                    st.session_state.player_id, from_pile, to_pile
                )
                
                if success:
                    st.success(message)
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(message)

def display_game_status(game_state):
    """Display game status."""
    # Current turn status
    current_player_idx = game_state.get('current_player', -1)
    current_player_name = game_state.get('current_player_name', 'Unknown')
    is_my_turn = False
    
    if (st.session_state.player_id and current_player_idx >= 0 and 
        game_state['players'][current_player_idx]['id'] == st.session_state.player_id):
        is_my_turn = True
    
    # Status display
    if is_my_turn:
        st.success("🎯 **YOUR TURN!** Play cards, move piles, then end your turn.")
    else:
        st.info(f"⏳ Waiting for **{current_player_name}** to play...")
    
    # Players info
    st.markdown("### 👥 Players")
    
    for i, player in enumerate(game_state['players']):
        icons = []
        if i == current_player_idx:
            icons.append("🎯")
        if player['id'] == st.session_state.player_id:
            icons.append("👤 (You)")
        
        status_text = " ".join(icons)
        st.write(f"**{player['name']}** - {player['hand_size']} cards {status_text}")
    
    return is_my_turn

def display_turn_controls(is_my_turn):
    """Display turn controls."""
    if not is_my_turn:
        return
    
    st.markdown("### ⚡ Turn Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ End Turn", key="end_turn", type="primary", use_container_width=True):
            if game_manager.end_turn(st.session_state.player_id):
                st.success("Turn ended!")
                st.session_state.selected_cards = []
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Could not end turn")
    
    with col2:
        if st.button("🔄 Refresh", key="refresh", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("📖 Rules", key="toggle_rules", use_container_width=True):
            st.session_state.show_rules = not st.session_state.show_rules
            st.rerun()

def display_rules():
    """Display game rules using native Streamlit."""
    if not st.session_state.show_rules:
        return
    
    with st.expander("📖 Kings in the Corner - Complete Rules", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Objective**")
            st.write("Be the first player to play all your cards.")
            
            st.markdown("**🎲 Setup**")
            st.write("• Each player gets 7 cards")
            st.write("• 4 foundation piles start with 1 card each")
            st.write("• 4 corner spaces start empty")
            
            st.markdown("**🃏 Foundation Piles**")
            st.write("• Build DOWN in alternating colors")
            st.write("• Red on Black, Black on Red")
            st.write("• When empty: ANY card can start new pile")
            st.write("• Example: Black 8 → Red 7 → Black 6")
        
        with col2:
            st.markdown("**👑 Corner Piles**")
            st.write("• Only KINGS can start corner piles")
            st.write("• Build down in alternating colors")
            st.write("• Same rules as foundations once started")
            
            st.markdown("**🔄 Moving Piles**")
            st.write("• Move entire piles between locations")
            st.write("• Bottom card must fit on destination")
            st.write("• Creates strategic opportunities")
            
            st.markdown("**⚡ Your Turn**")
            st.write("• Play as many cards as you want")
            st.write("• Move piles between locations")
            st.write("• End turn OR draw a card (ends turn)")

def main_menu():
    """Main menu interface."""
    st.title("🃏 Kings in the Corner")
    st.subheader("Complete Multiplayer Card Game")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Player name
        player_name = st.text_input(
            "👤 Your name:",
            value=st.session_state.player_name,
            placeholder="Enter your name..."
        )
        if player_name:
            st.session_state.player_name = player_name
        
        st.markdown("---")
        
        # Game actions
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### 🆕 New Game")
            if st.button("Create Game", disabled=not player_name, use_container_width=True, type="primary"):
                try:
                    game_id, player_id = game_manager.create_game(player_name)
                    st.session_state.game_id = game_id
                    st.session_state.player_id = player_id
                    st.balloons()
                    st.success(f"Game created! ID: **{game_id[:8]}...**")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col_b:
            st.markdown("#### 🔗 Join Game")
            game_id_input = st.text_input("Game ID:", placeholder="Enter game ID...")
            if st.button("Join Game", disabled=not (player_name and game_id_input), use_container_width=True):
                try:
                    player_id = game_manager.join_game(game_id_input, player_name)
                    if player_id:
                        st.session_state.game_id = game_id_input
                        st.session_state.player_id = player_id
                        st.success("Joined game!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Could not join game!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Features
        st.markdown("---")
        st.markdown("#### ✨ Game Features")
        st.write("🎯 Multiple cards per turn - Play as many as you want")
        st.write("🔄 Pile moving - Move entire stacks strategically")
        st.write("📚 Visual stacking - See all cards in piles")
        st.write("📱 Cross-platform - Works on any device")
        st.write("⚡ Real-time - Instant multiplayer updates")

def game_lobby(game_state):
    """Game lobby interface."""
    st.title("🎮 Game Lobby")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Share this Game ID:")
        st.code(st.session_state.game_id)
        
        st.markdown("### 👥 Players")
        for i, player in enumerate(game_state['players']):
            emoji = "👑" if player['id'] == st.session_state.player_id else "👤"
            host = " (Host)" if i == 0 else ""
            you = " (You)" if player['id'] == st.session_state.player_id else ""
            st.write(f"{emoji} **{player['name']}**{host}{you}")
        
        player_count = len(game_state['players'])
        st.info(f"Players: {player_count}/4 (minimum 2 to start)")
        
        if player_count >= 2:
            if st.button("🚀 Start Game", use_container_width=True, type="primary"):
                try:
                    if game_manager.start_game(st.session_state.game_id, st.session_state.player_id):
                        st.balloons()
                        st.success("Game started!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Could not start game")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("⏳ Waiting for more players...")

def main_game_interface(game_state):
    """Main game interface."""
    # Find player data
    player_data = None
    for player in game_state['players']:
        if player['id'] == st.session_state.player_id:
            player_data = player
            break
    
    # Game status
    is_my_turn = display_game_status(game_state)
    
    # Rules
    display_rules()
    
    # Game board
    display_game_board(game_state)
    
    # Player interface (only on their turn)
    if is_my_turn:
        # Hand
        display_hand_interface(player_data)
        
        # Actions
        display_actions_interface(game_state)
        
        # Turn controls
        display_turn_controls(is_my_turn)
    
    else:
        # Show limited info when not player's turn
        if player_data and player_data['hand']:
            st.markdown("### 🃏 Your Hand")
            hand_summary = []
            for card in player_data['hand']:
                hand_summary.append(get_card_display(card))
            st.info(f"Cards ({len(player_data['hand'])}): {', '.join(hand_summary)}")

def main():
    """Main application."""
    init_session_state()
    
    # Auto-refresh for multiplayer
    st_autorefresh(interval=3000, key="main_refresh")
    
    # Navigation
    try:
        if not st.session_state.game_id or not st.session_state.player_id:
            main_menu()
        else:
            game_state = game_manager.get_game_state(st.session_state.game_id)
            
            if not game_state:
                st.error("⚠️ Game not found!")
                if st.button("🏠 Back to Menu"):
                    st.session_state.game_id = None
                    st.session_state.player_id = None
                    st.session_state.selected_cards = []
                    st.rerun()
                return
            
            if game_state['game_over']:
                st.balloons()
                st.success(f"🎉 **{game_state['winner']}** wins!")
                if st.button("🏠 New Game"):
                    st.session_state.game_id = None
                    st.session_state.player_id = None
                    st.session_state.selected_cards = []
                    st.rerun()
                return
            
            if not game_state['game_started']:
                game_lobby(game_state)
            else:
                main_game_interface(game_state)
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        if st.button("🏠 Return to Menu"):
            st.session_state.game_id = None
            st.session_state.player_id = None
            st.session_state.selected_cards = []
            st.rerun()

if __name__ == "__main__":
    main()
