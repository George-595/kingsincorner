"""
Kings in the Corner - Complete Unified Game
All features in one app with proper game rules implementation
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
    """Initialize all session state variables."""
    defaults = {
        'player_id': None,
        'game_id': None,
        'player_name': "",
        'selected_cards': [],
        'last_action': None,
        'show_rules': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def apply_game_styles():
    """Apply comprehensive CSS styling for the game."""
    st.markdown("""
    <style>
    /* Main Layout */
    .main > div { padding-top: 1rem; }
    .block-container { padding-top: 1rem; max-width: 1200px; }
    
    /* Card Styling */
    .card {
        display: inline-block;
        background: white;
        border: 2px solid #333;
        border-radius: 8px;
        padding: 6px 10px;
        margin: 3px;
        font-weight: bold;
        text-align: center;
        min-width: 45px;
        font-size: 13px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
        cursor: pointer;
        user-select: none;
    }
    
    .card:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 3px 3px 10px rgba(0,0,0,0.3);
        z-index: 10;
    }
    
    .card-red { color: #d32f2f; border-color: #d32f2f; }
    .card-black { color: #333; border-color: #333; }
    .card-selected { 
        border-color: #4CAF50 !important; 
        background: #e8f5e8 !important; 
        border-width: 3px !important;
        transform: translateY(-2px);
    }
    
    /* Game Board */
    .game-board {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .pile-container {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 15px;
        margin: 5px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .pile-container:hover {
        border-color: rgba(255, 255, 255, 0.6);
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
    }
    
    .pile-foundation { border-color: rgba(76, 175, 80, 0.5); }
    .pile-corner { border-color: rgba(255, 193, 7, 0.5); }
    .pile-empty { border-style: dashed; }
    .pile-has-cards { border-style: solid; border-width: 3px; }
    
    .pile-title {
        color: white;
        font-weight: bold;
        font-size: 11px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.9;
    }
    
    .pile-count {
        color: rgba(255, 255, 255, 0.7);
        font-size: 10px;
        margin-top: 5px;
    }
    
    /* Card Stacking */
    .card-stack {
        position: relative;
        min-height: 70px;
        min-width: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .stacked-card {
        position: absolute;
        font-size: 11px;
        padding: 4px 6px;
        min-width: 35px;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    /* Deck Styling */
    .deck-container {
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        border: none !important;
        color: white;
        cursor: pointer;
    }
    
    .deck-container:hover {
        background: linear-gradient(45deg, #45a049, #4CAF50) !important;
        transform: scale(1.05);
    }
    
    .deck-icon { font-size: 28px; margin: 5px 0; }
    
    /* Hand Container */
    .hand-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .hand-title {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
        color: #333;
    }
    
    .hand-cards {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        align-items: center;
    }
    
    /* Status and UI Elements */
    .status-container {
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        margin: 20px 0;
        font-weight: bold;
        font-size: 16px;
    }
    
    .status-my-turn {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .status-waiting {
        background: linear-gradient(45deg, #FF9800, #F57C00);
        color: white;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .player-info {
        display: inline-block;
        background: rgba(255, 255, 255, 0.9);
        padding: 8px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
        color: #333;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .player-current {
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        color: white !important;
        animation: glow 2s infinite;
    }
    
    .player-me {
        background: linear-gradient(45deg, #2196F3, #1976D2) !important;
        color: white !important;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3); }
        50% { box-shadow: 0 4px 16px rgba(76, 175, 80, 0.6); }
    }
    
    /* Action Sections */
    .action-section {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .action-title {
        font-size: 16px;
        font-weight: bold;
        color: #333;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .game-board { padding: 15px; }
        .pile-container { min-height: 100px; padding: 10px; }
        .card { padding: 4px 8px; font-size: 11px; min-width: 40px; }
        .hand-cards { gap: 5px; }
    }
    
    /* Animations */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Success/Error Messages */
    .message-success {
        background: #4CAF50;
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    
    .message-error {
        background: #f44336;
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* Rules Panel */
    .rules-panel {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border-left: 5px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

def get_card_html(card, card_id="", clickable=False, stacked_offset=0):
    """Generate HTML for a single card."""
    if not card:
        return ""
    
    color_class = "card-red" if card['color'] == 'red' else "card-black"
    selected_class = "card-selected" if f"{card['rank']}{card['suit']}" in st.session_state.selected_cards else ""
    
    style = ""
    if stacked_offset > 0:
        style = f"transform: translate({stacked_offset*3}px, {stacked_offset*3}px); z-index: {10-stacked_offset};"
    
    click_attr = f'onclick="toggleCardSelection(\'{card["rank"]}{card["suit"]}\')"' if clickable else ""
    
    return f'''
    <div class="card {color_class} {selected_class}" id="{card_id}" {click_attr} style="{style}">
        <div>{card["rank"]}</div>
        <div>{card["suit"]}</div>
    </div>
    '''

def display_pile(pile_data, pile_name, pile_type="foundation"):
    """Display a game pile with proper stacking and rules."""
    cards = pile_data.get('cards', [])
    is_empty = len(cards) == 0
    
    # Determine pile styling
    pile_classes = ["pile-container"]
    if pile_type == "corner":
        pile_classes.append("pile-corner")
    else:
        pile_classes.append("pile-foundation")
    
    if is_empty:
        pile_classes.append("pile-empty")
    else:
        pile_classes.append("pile-has-cards")
    
    # Title with proper formatting
    display_name = pile_name.replace('_', ' ').title()
    if pile_type == "corner":
        display_name += " Corner"
    else:
        display_name += " Foundation"
    
    # Create stacked cards display
    cards_html = ""
    if cards:
        # Show last 4 cards with stacking effect
        visible_cards = cards[-4:] if len(cards) > 4 else cards
        for i, card in enumerate(visible_cards):
            cards_html += get_card_html(card, f"{pile_name}_card_{i}", False, i)
        
        if len(cards) > 4:
            cards_html = f'<div style="font-size: 9px; color: rgba(255,255,255,0.6); margin-bottom: 3px;">+{len(cards)-4} more</div>' + cards_html
    else:
        # Empty pile indicators
        if pile_type == "corner":
            cards_html = '<div style="color: rgba(255,255,255,0.5); font-size: 11px;">Kings Only</div>'
        else:
            cards_html = '<div style="color: rgba(255,255,255,0.5); font-size: 11px;">Any Card</div>'
    
    # Count display
    count_text = f"{len(cards)} cards" if len(cards) != 1 else "1 card"
    if len(cards) == 0:
        count_text = "Empty"
    
    return f'''
    <div class="{' '.join(pile_classes)}">
        <div class="pile-title">{display_name}</div>
        <div class="card-stack">
            {cards_html}
        </div>
        <div class="pile-count">{count_text}</div>
    </div>
    '''

def display_game_board(game_state):
    """Display the complete game board with 3x3 layout."""
    st.markdown('<div class="game-board fade-in">', unsafe_allow_html=True)
    
    # 3x3 Grid Layout
    board_layout = [
        [('nw', 'corner'), ('north', 'foundation'), ('ne', 'corner')],
        [('west', 'foundation'), ('deck', 'deck'), ('east', 'foundation')],
        [('sw', 'corner'), ('south', 'foundation'), ('se', 'corner')]
    ]
    
    for row in board_layout:
        cols = st.columns(3)
        for i, (position, pos_type) in enumerate(row):
            with cols[i]:
                if position == 'deck':
                    # Special deck display
                    deck_size = game_state['deck_size']
                    deck_html = f'''
                    <div class="pile-container deck-container">
                        <div class="pile-title">Draw Pile</div>
                        <div class="deck-icon">🃏</div>
                        <div style="font-size: 12px; font-weight: bold;">{deck_size} cards</div>
                    </div>
                    '''
                    st.markdown(deck_html, unsafe_allow_html=True)
                    
                    if st.button("🃏 Draw Card", key="draw_main", use_container_width=True):
                        success, message = game_manager.draw_card(st.session_state.player_id)
                        if success:
                            st.success(message)
                            time.sleep(0.3)
                            st.rerun()
                        else:
                            st.error(message)
                
                elif pos_type == 'corner':
                    # Corner piles
                    pile_data = game_state['corner_piles'][position]
                    pile_html = display_pile(pile_data, position, 'corner')
                    st.markdown(pile_html, unsafe_allow_html=True)
                
                else:
                    # Foundation piles
                    pile_data = game_state['foundation_piles'][position]
                    pile_html = display_pile(pile_data, position, 'foundation')
                    st.markdown(pile_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_hand_interface(player_data):
    """Display player hand with selection capabilities."""
    if not player_data or not player_data['hand']:
        st.info("🃏 No cards in hand")
        return
    
    st.markdown('<div class="hand-container fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="hand-title">🃏 Your Hand - Click to Select Cards</div>', unsafe_allow_html=True)
    
    # Display cards with selection
    cards_per_row = 10
    hand = player_data['hand']
    
    st.markdown('<div class="hand-cards">', unsafe_allow_html=True)
    for i, card in enumerate(hand):
        card_id = f"{card['rank']}{card['suit']}"
        is_selected = card_id in st.session_state.selected_cards
        
        # Create button with selection state
        button_text = f"{'🎯 ' if is_selected else ''}{card['rank']}{card['suit']}"
        button_type = "primary" if is_selected else "secondary"
        
        if st.button(button_text, key=f"hand_card_{i}", type=button_type):
            if is_selected:
                st.session_state.selected_cards.remove(card_id)
            else:
                st.session_state.selected_cards.append(card_id)
            st.rerun()
        
        # Add line break every cards_per_row cards
        if (i + 1) % cards_per_row == 0:
            st.markdown('<br>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show selected cards summary
    if st.session_state.selected_cards:
        selected_text = ", ".join(st.session_state.selected_cards)
        st.markdown(f'<div class="message-success">Selected: {selected_text}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_card_actions(game_state):
    """Display card playing interface."""
    if not st.session_state.selected_cards:
        st.info("👆 Select cards from your hand first to play them!")
        return
    
    st.markdown('<div class="action-section fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="action-title">🎯 Play Selected Cards</div>', unsafe_allow_html=True)
    
    # Get all available piles
    all_piles = (list(game_state['foundation_piles'].keys()) + 
                list(game_state['corner_piles'].keys()))
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        target_pile = st.selectbox(
            "Choose destination pile:",
            all_piles,
            format_func=lambda x: f"{x.replace('_', ' ').title()} ({'Corner' if x in game_state['corner_piles'] else 'Foundation'})",
            key="play_target_pile"
        )
    
    with col2:
        if st.button("🃏 Play Selected Cards", key="play_cards_btn", type="primary", use_container_width=True):
            success_count = 0
            failed_cards = []
            
            # Sort selected cards to play in optimal order
            selected_copy = st.session_state.selected_cards.copy()
            
            for card_id in selected_copy:
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
                    break  # Stop on first failure to maintain game integrity
            
            # Show results
            if success_count > 0:
                st.success(f"✅ Successfully played {success_count} card(s)!")
            
            if failed_cards:
                st.error(f"❌ {failed_cards[0]}")
            
            if success_count > 0:
                time.sleep(0.5)
                st.rerun()
    
    with col3:
        if st.button("🧹 Clear Selection", key="clear_cards", use_container_width=True):
            st.session_state.selected_cards = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_pile_actions(game_state):
    """Display pile moving interface with proper rules."""
    st.markdown('<div class="action-section fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="action-title">🔄 Move Entire Piles</div>', unsafe_allow_html=True)
    
    # Get all piles and their status
    all_piles = (list(game_state['foundation_piles'].keys()) + 
                list(game_state['corner_piles'].keys()))
    
    # Find moveable piles (non-empty)
    moveable_piles = []
    for pile_name in all_piles:
        if pile_name in game_state['foundation_piles']:
            pile = game_state['foundation_piles'][pile_name]
        else:
            pile = game_state['corner_piles'][pile_name]
        
        if pile['cards']:
            moveable_piles.append(pile_name)
    
    if not moveable_piles:
        st.info("No piles available to move")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    col1, col2, col3 = st.columns([3, 3, 2])
    
    with col1:
        from_pile = st.selectbox(
            "From pile:",
            moveable_piles,
            format_func=lambda x: f"{x.replace('_', ' ').title()} ({'Corner' if x in game_state['corner_piles'] else 'Foundation'})",
            key="move_from_pile"
        )
    
    with col2:
        # All piles except the source pile
        target_piles = [p for p in all_piles if p != from_pile]
        to_pile = st.selectbox(
            "To pile:",
            target_piles,
            format_func=lambda x: f"{x.replace('_', ' ').title()} ({'Corner' if x in game_state['corner_piles'] else 'Foundation'})",
            key="move_to_pile"
        )
    
    with col3:
        if st.button("🔄 Move Pile", key="execute_move", type="primary", use_container_width=True):
            success, message = game_manager.move_pile(
                st.session_state.player_id, from_pile, to_pile
            )
            
            if success:
                st.success(message)
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(message)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_game_status(game_state):
    """Display comprehensive game status."""
    # Current player and turn status
    current_player_idx = game_state.get('current_player', -1)
    current_player_name = game_state.get('current_player_name', 'Unknown')
    is_my_turn = False
    
    if (st.session_state.player_id and current_player_idx >= 0 and 
        game_state['players'][current_player_idx]['id'] == st.session_state.player_id):
        is_my_turn = True
    
    # Status banner
    if is_my_turn:
        st.markdown('''
        <div class="status-container status-my-turn fade-in">
            🎯 <strong>Your Turn!</strong> Play cards, move piles, then end your turn or draw a card.
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="status-container status-waiting fade-in">
            ⏳ Waiting for <strong>{current_player_name}</strong> to play...
        </div>
        ''', unsafe_allow_html=True)
    
    # Players information
    st.markdown("### 👥 Players")
    players_html = '<div style="text-align: center; margin: 15px 0;">'
    
    for i, player in enumerate(game_state['players']):
        classes = ["player-info"]
        if i == current_player_idx:
            classes.append("player-current")
        if player['id'] == st.session_state.player_id:
            classes.append("player-me")
        
        status_icon = " 🎯" if i == current_player_idx else ""
        me_indicator = " (You)" if player['id'] == st.session_state.player_id else ""
        
        players_html += f'''
        <span class="{' '.join(classes)}">
            {player['name']}{me_indicator} - {player['hand_size']} cards{status_icon}
        </span>
        '''
    
    players_html += '</div>'
    st.markdown(players_html, unsafe_allow_html=True)
    
    return is_my_turn

def display_turn_controls(is_my_turn):
    """Display turn control buttons."""
    if not is_my_turn:
        return
    
    st.markdown("---")
    st.markdown("### ⚡ Turn Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ End Turn", key="end_turn_btn", type="primary", use_container_width=True):
            if game_manager.end_turn(st.session_state.player_id):
                st.success("Turn ended!")
                st.session_state.selected_cards = []  # Clear selections
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Could not end turn")
    
    with col2:
        if st.button("🔄 Refresh Game", key="manual_refresh", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("📖 Rules", key="toggle_rules", use_container_width=True):
            st.session_state.show_rules = not st.session_state.show_rules
            st.rerun()

def display_game_rules():
    """Display comprehensive game rules."""
    if not st.session_state.show_rules:
        return
    
    st.markdown('''
    <div class="rules-panel fade-in">
        <h3 style="color: #4CAF50; margin-bottom: 20px;">📖 Kings in the Corner - Complete Rules</h3>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h4>🎯 Objective</h4>
                <p>Be the first player to get rid of all your cards by playing them onto foundation and corner piles.</p>
                
                <h4>🎲 Setup</h4>
                <ul>
                    <li>Each player gets 7 cards</li>
                    <li>4 foundation piles start with 1 card each</li>
                    <li>4 corner spaces start empty (Kings only)</li>
                    <li>Remaining cards form the draw pile</li>
                </ul>
                
                <h4>🃏 Foundation Piles</h4>
                <ul>
                    <li>Build DOWN in alternating colors</li>
                    <li>Red on Black, Black on Red</li>
                    <li>When empty: ANY card can start a new pile</li>
                    <li>Example: Black 8 → Red 7 → Black 6</li>
                </ul>
            </div>
            
            <div>
                <h4>👑 Corner Piles</h4>
                <ul>
                    <li>Only KINGS can start corner piles</li>
                    <li>Build DOWN in alternating colors</li>
                    <li>Same rules as foundation piles once started</li>
                </ul>
                
                <h4>🔄 Moving Piles</h4>
                <ul>
                    <li>Move entire piles between locations</li>
                    <li>Bottom card must fit on destination</li>
                    <li>Creates strategic opportunities</li>
                    <li>Empty foundations accept any card</li>
                </ul>
                
                <h4>⚡ Turn Actions</h4>
                <ul>
                    <li>Play as many cards as possible</li>
                    <li>Move piles between locations</li>
                    <li>End turn OR draw a card (ends turn)</li>
                    <li>First to empty hand wins!</li>
                </ul>
            </div>
        </div>
        
        <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <strong>💡 Strategy Tips:</strong> Look for pile moving opportunities! Moving a pile can create new empty foundations that accept any card, giving you more playing options.
        </div>
    </div>
    ''', unsafe_allow_html=True)

def main_menu():
    """Enhanced main menu with better styling."""
    apply_game_styles()
    
    st.markdown('''
    <div style="text-align: center; padding: 40px 20px;" class="fade-in">
        <h1 style="color: #4CAF50; font-size: 4em; margin-bottom: 20px;">🃏</h1>
        <h2 style="color: #333; margin-bottom: 10px;">Kings in the Corner</h2>
        <h4 style="color: #666; margin-bottom: 40px;">Complete Multiplayer Edition</h4>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Player name input
        player_name = st.text_input(
            "👤 Enter your name:",
            value=st.session_state.player_name,
            placeholder="Your name here...",
            key="player_name_input"
        )
        if player_name != st.session_state.player_name:
            st.session_state.player_name = player_name
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Game creation/joining
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🆕 Create New Game", 
                        disabled=not player_name, 
                        use_container_width=True,
                        type="primary"):
                try:
                    game_id, player_id = game_manager.create_game(player_name)
                    st.session_state.game_id = game_id
                    st.session_state.player_id = player_id
                    st.balloons()
                    st.success(f"🎉 Game created! Share ID: **{game_id[:8]}...**")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to create game: {e}")
        
        with col_b:
            game_id_input = st.text_input(
                "🔗 Enter Game ID:",
                placeholder="Paste game ID here...",
                key="game_id_input"
            )
            if st.button("Join Game", 
                        disabled=not (player_name and game_id_input), 
                        use_container_width=True):
                try:
                    player_id = game_manager.join_game(game_id_input, player_name)
                    if player_id:
                        st.session_state.game_id = game_id_input
                        st.session_state.player_id = player_id
                        st.success("✅ Successfully joined the game!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Could not join game. Check the Game ID!")
                except Exception as e:
                    st.error(f"Failed to join game: {e}")
        
        # Features showcase
        st.markdown("---")
        st.markdown('''
        <div style="text-align: center;">
            <h4>✨ Complete Features</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                <div style="background: rgba(76, 175, 80, 0.1); padding: 15px; border-radius: 10px;">
                    <strong>🎯 Multi-Card Play</strong><br>
                    <small>Select and play multiple cards per turn</small>
                </div>
                <div style="background: rgba(33, 150, 243, 0.1); padding: 15px; border-radius: 10px;">
                    <strong>🔄 Pile Moving</strong><br>
                    <small>Move entire piles strategically</small>
                </div>
                <div style="background: rgba(255, 152, 0, 0.1); padding: 15px; border-radius: 10px;">
                    <strong>📚 Visual Stacking</strong><br>
                    <small>See all cards in each pile</small>
                </div>
                <div style="background: rgba(156, 39, 176, 0.1); padding: 15px; border-radius: 10px;">
                    <strong>📱 Cross-Platform</strong><br>
                    <small>Works on phones, tablets, computers</small>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

def game_lobby(game_state):
    """Enhanced game lobby interface."""
    apply_game_styles()
    
    st.markdown(f'''
    <div style="text-align: center; padding: 30px;" class="fade-in">
        <h2>🎮 Game Lobby</h2>
        <p style="margin: 20px 0;">Share this Game ID with your friends:</p>
        <div style="background: #f0f0f0; padding: 15px 20px; border-radius: 10px; display: inline-block; margin: 10px 0;">
            <code style="font-size: 18px; font-weight: bold; color: #4CAF50;">{st.session_state.game_id}</code>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👥 Players in Game")
        
        # Display players with enhanced styling
        for i, player in enumerate(game_state['players']):
            emoji = "👑" if player['id'] == st.session_state.player_id else "👤"
            status = " (Host)" if i == 0 else ""
            if player['id'] == st.session_state.player_id:
                st.markdown(f"**🔵 {emoji} {player['name']}{status} (You)**")
            else:
                st.markdown(f"**⚪ {emoji} {player['name']}{status}**")
        
        player_count = len(game_state['players'])
        
        if player_count < 4:
            st.info(f"**{player_count}/4 players joined** - Waiting for more players...")
        else:
            st.success(f"**{player_count}/4 players** - Ready to start!")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Start game button
        if player_count >= 2:
            if st.button("🚀 Start Kings in the Corner!", 
                        use_container_width=True, 
                        type="primary"):
                try:
                    if game_manager.start_game(st.session_state.game_id, st.session_state.player_id):
                        st.balloons()
                        st.success("🎉 Game started! Good luck!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Could not start the game")
                except Exception as e:
                    st.error(f"Failed to start game: {e}")
        else:
            st.warning("⏳ Need at least 2 players to start the game")
        
        # Rules preview
        if st.button("📖 View Rules", key="lobby_rules", use_container_width=True):
            st.session_state.show_rules = True
            st.rerun()

def main_game_interface(game_state):
    """Complete main game interface."""
    apply_game_styles()
    
    # Find current player data
    player_data = None
    for player in game_state['players']:
        if player['id'] == st.session_state.player_id:
            player_data = player
            break
    
    # Game status and turn information
    is_my_turn = display_game_status(game_state)
    
    # Rules display (toggleable)
    display_game_rules()
    
    # Main game board
    st.markdown("## 🎲 Game Board")
    display_game_board(game_state)
    
    # Player actions (only show detailed interface on player's turn)
    if is_my_turn:
        # Player hand with selection
        display_hand_interface(player_data)
        
        # Action interfaces in columns
        col1, col2 = st.columns(2)
        
        with col1:
            display_card_actions(game_state)
        
        with col2:
            display_pile_actions(game_state)
        
        # Turn controls
        display_turn_controls(is_my_turn)
    
    else:
        # Show limited hand view when not player's turn
        if player_data and player_data['hand']:
            st.markdown("### 🃏 Your Hand")
            hand_summary = " ".join([f"{card['rank']}{card['suit']}" for card in player_data['hand']])
            st.info(f"Your cards ({len(player_data['hand'])}): {hand_summary}")
        
        # Show rules toggle for non-active players
        if st.button("📖 Toggle Rules", key="waiting_rules"):
            st.session_state.show_rules = not st.session_state.show_rules
            st.rerun()

def main():
    """Main application entry point."""
    init_session_state()
    
    # Auto-refresh for real-time multiplayer experience
    st_autorefresh(interval=3000, key="unified_game_refresh")
    
    # Navigation logic
    try:
        if not st.session_state.game_id or not st.session_state.player_id:
            main_menu()
        else:
            # Get current game state
            game_state = game_manager.get_game_state(st.session_state.game_id)
            
            if not game_state:
                st.error("⚠️ Game not found! Returning to main menu...")
                # Reset session
                st.session_state.game_id = None
                st.session_state.player_id = None
                st.session_state.selected_cards = []
                time.sleep(2)
                st.rerun()
                return
            
            # Check for game over
            if game_state['game_over']:
                apply_game_styles()
                st.balloons()
                st.markdown(f'''
                <div style="text-align: center; padding: 50px;" class="fade-in">
                    <h1 style="color: #4CAF50;">🎉 Game Over!</h1>
                    <h2 style="color: #333;">Winner: <strong style="color: #4CAF50;">{game_state['winner']}</strong></h2>
                    <p style="color: #666; margin: 20px 0;">Congratulations on a great game!</p>
                </div>
                ''', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🏠 Return to Main Menu", use_container_width=True, type="primary"):
                        st.session_state.game_id = None
                        st.session_state.player_id = None
                        st.session_state.selected_cards = []
                        st.session_state.show_rules = False
                        st.rerun()
                return
            
            # Game flow
            if not game_state['game_started']:
                game_lobby(game_state)
            else:
                main_game_interface(game_state)
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Try refreshing the page or returning to the main menu.")
        if st.button("🏠 Return to Main Menu"):
            st.session_state.game_id = None
            st.session_state.player_id = None
            st.session_state.selected_cards = []
            st.rerun()

if __name__ == "__main__":
    main()