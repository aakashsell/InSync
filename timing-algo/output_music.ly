\version "2.24.4"
% automatically converted by musicxml2ly from output_music.mxl
\pointAndClickOff

\header {
    }

\layout {
    \context { \Score
        autoBeaming = ##f
        }
    }
PartPOneVoiceOne =  \relative c'' {
    r1*3/4 r1*3/4 r1*1/4 c1*1/4 c1*1/2 <f a,>1*0 b,1*3/4 c1*1/2 <a c>1*0
    r1*0 b1*1/4 b1*1/4 a1*1/4 a1*1/4 g1*1/4 <b a d c c>1*0 r1*0 b1*1/4 b1*1/4
    a1*1/4 a1*1/4 g1*1/4 f1*1/4 f1*1/4 r1*3/4 r1*3/4 r1*5/2 r1*3/4 r1*3/4
    r1*1/4 c'1*1/4 c1*1/2 <a a>1*0 r1*1/4 c1*1/4 c1*1/2 <g g>1*0 r1*1/4
    e'1*1/4 <e d f d c>1*0 d1*1/4 c1*3/4 r1*3/4 r1*1/4 g'1*1/4 g1*1/2
    <b, b>1*0 a1*3/4 a1*3/4 g1*3/4 r1*1/4 g'1*1/4 g1*1/2 <b, b>1*0 a1*3/4
    a1*3/4 g1*3/4 r1*1/4 c1*1/4 d1*3/4 b1*3/4 r1*1/4 d1*1/4 c1*3/4 a1*3/4
    r1*1/4 a1*1/4 <a g b g f>1*0 g1*1/4 g1*3/4 a1*3/4 r1*1/4 c1*1/4 d1*3/4
    b1*3/4 r1*1/4 d1*1/4 c1*3/4 a1*3/4 r1*1/4 a1*1/4 <a g b g f>1*0 g1*3/4
    c1*3/2 c1*3/4 d1*1/4 <e f a,>1*0 <b c c,>1*0 <d, e f>1*0 r1*3/4 r1*5/2
    r1*3/4 r1*3/4 r1*1/4 c'1*1/4 c1*1/2 <e e>1*0 <d c c>1*0 b1*3/4 r1*1/4
    g1*1/4 g1*1/2 <f' f>1*0 d1*1/4 d1*1/4 c1*1/4 c1*3/4 r1*1/4 g'1*1/4 g1*1/4
    f1*1/4 e1*1/4 d1*1/4 c1*1/4 b1*1/4 a1*1/2 <f' f>1*0 r1*1/4 e1*1/4 <e
        d f d c>1*0 b1*3/4 c1*1/4 <c d e>1*0 <e f g>1*0 e1*1/4 <e d f d
        c>1*0 b1*3/4 c1*1/4 <c d e>1*0 <e f g>1*0 e1*1/4 <e d f a c,>1*0
    e1*1/4 d1*1/4 c1*3/2 r1*1/4 c1*1/4 c1*1/2 <f a,>1*0 b,1*3/4 c1*1/2
    <a c>1*0 r1*0 b1*1/4 b1*1/4 a1*1/4 a1*1/4 g1*1/4 <b a d c c>1*0 r1*0
    b1*1/4 b1*1/4 a1*1/4 a1*1/4 g1*1/4 f1*1/4 f1*1/4 r1*3/4 r1*3/4 r1*5/2
    r1*3/4 r1*3/4 r1*1/4 c'1*1/4 c1*1/2 <a a>1*0 r1*1/4 c1*1/4 c1*1/2 <g
        g>1*0 r1*1/4 e'1*1/4 <e d f d c>1*0 d1*1/4 c1*3/4 r1*3/4 r1*1/4
    g'1*1/4 g1*1/2 <b, b>1*0 a1*3/4 a1*3/4 g1*3/4 r1*1/4 g'1*1/4 g1*1/2
    <b, b>1*0 a1*3/4 a1*3/4 g1*3/4 r1*1/4 c1*1/4 d1*3/4 b1*3/4 r1*1/4 d1*1/4
    c1*3/4 a1*3/4 r1*1/4 a1*1/4 <a g b g f>1*0 g1*1/4 g1*3/4 a1*3/4 r1*1/4
    c1*1/4 d1*3/4 b1*3/4 r1*1/4 d1*1/4 c1*3/4 a1*3/4 r1*1/4 a1*1/4 <a g
        b g f>1*0 g1*3/4 c1*3/2 c1*3/4 d1*1/4 <e f a,>1*0 <b c c,>1*0
    <d, e f>1*0 r1*3/4 r1*5/2 r1*5/2 r1*5/2 }


% The score definition
\score {
    <<
        
        \new Staff
        <<
            \set Staff.instrumentName = "Part P1"
            
            \context Staff << 
                \mergeDifferentlyDottedOn\mergeDifferentlyHeadedOn
                \context Voice = "PartPOneVoiceOne" {  \PartPOneVoiceOne }
                >>
            >>
        
        >>
    \layout {}
    % To create MIDI output, uncomment the following line:
    %  \midi {\tempo 4 = 100 }
    }

