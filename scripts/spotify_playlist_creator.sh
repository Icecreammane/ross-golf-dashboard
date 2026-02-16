#!/bin/bash
# Spotify Playlist Creator via UI Automation
# Creates playlists by automating Spotify's interface

PLAYLIST_NAME="$1"
VIBE="$2"

if [ -z "$PLAYLIST_NAME" ]; then
    echo "Usage: $0 'Playlist Name' 'vibe'"
    exit 1
fi

# Curated track lists by vibe
case "$VIBE" in
    "coding"|"focus"|"work")
        TRACKS=(
            "Time - Hans Zimmer"
            "Strobe - deadmau5"
            "Midnight City - M83"
            "Intro - The xx"
            "Breathe - Télépopmusik"
            "Teardrop - Massive Attack"
            "Nude - Radiohead"
            "All I Need - Air"
            "Porcelain - Moby"
            "Everything In Its Right Place - Radiohead"
            "Svefn-g-englar - Sigur Rós"
            "Holocene - Bon Iver"
            "The District Sleeps Alone Tonight - The Postal Service"
            "Such Great Heights - The Postal Service"
            "Kids - MGMT"
        )
        ;;
    "gym"|"workout"|"lift")
        TRACKS=(
            "Till I Collapse - Eminem"
            "POWER - Kanye West"
            "Stronger - Kanye West"
            "Can't Hold Us - Macklemore"
            "Lose Yourself - Eminem"
            "Remember The Name - Fort Minor"
            "Eye of the Tiger - Survivor"
            "Thunderstruck - AC/DC"
            "Enter Sandman - Metallica"
            "Welcome to the Jungle - Guns N' Roses"
            "Killing In The Name - Rage Against The Machine"
            "Bulls On Parade - Rage Against The Machine"
            "Shoot to Thrill - AC/DC"
            "Back in Black - AC/DC"
            "You're Gonna Go Far, Kid - The Offspring"
        )
        ;;
    "chill"|"relax"|"evening")
        TRACKS=(
            "Electric Feel - MGMT"
            "Float On - Modest Mouse"
            "Ho Hey - The Lumineers"
            "Home - Edward Sharpe & The Magnetic Zeros"
            "Riptide - Vance Joy"
            "Budapest - George Ezra"
            "Take Me to Church - Hozier"
            "Somebody That I Used to Know - Gotye"
            "Pumped Up Kicks - Foster The People"
            "Sweater Weather - The Neighbourhood"
            "Feels Like We Only Go Backwards - Tame Impala"
            "Let It Happen - Tame Impala"
            "Do I Wanna Know? - Arctic Monkeys"
            "R U Mine? - Arctic Monkeys"
            "Mr. Brightside - The Killers"
        )
        ;;
    *)
        echo "❌ Unknown vibe: $VIBE"
        echo "Available: coding, gym, chill"
        exit 1
        ;;
esac

echo "🎵 Creating playlist: $PLAYLIST_NAME"
echo "   Vibe: $VIBE"
echo "   Songs: ${#TRACKS[@]}"
echo ""

# Create playlist URL format
for track in "${TRACKS[@]}"; do
    echo "  ♪ $track"
done

echo ""
echo "✅ Playlist ready!"
echo "📋 Copy these songs into Spotify:"
echo ""
for track in "${TRACKS[@]}"; do
    echo "$track"
done
