

document.addEventListener("DOMContentLoaded", function() {
    // ---------------------------------------------MANAGING SIDEBAR--------------------------------------------- // 
    
    screenWidth = window.innerWidth;
 
    // Fuction for the sidebar toggle button
    toggleSidebarButton.addEventListener('click', function toggleSidebar() {
        // Toggle of class 'collapsed' of sidebar
        
        toggleSidebarButton.style.visibility = 'hidden';
        closeSidebarButton.style.visibility = 'visible';
        isSidebarClosed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isSidebarClosed) {
            console.log('sidebar aperta al click del bottone');
            openSidebar();
        } else {
            console.log('sidebar chiusa al click del bottone');
            closeSidebar();
        }
    });

    // Function for the close sidebar button
    closeSidebarButton.addEventListener('click', function closeSidebarBtn() {
        isSidebarClosed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (!isSidebarClosed) {
            console.log('sidebar chiusa al click del bottone');
            closeSidebar();
        }
    });
    
    // Fuction to manage the sidebar state on window resize
    window.addEventListener('resize', function() {

        screenWidth = window.innerWidth;
        isSidebarClosed = localStorage.getItem('sidebarCollapsed') === 'true';
        // console.log(isSidebarCollapsed);
        if (window.innerWidth <= screenLimit) {
            // If the window is smaller than screenLimit
            if (!isSidebarClosed) {
                console.log('sidebar chiusa al ridimensionamento della pagina');
                closeSidebar();
            }
        } /* else {
            // If the window is larger than screenLimit
            if (isSidebarClosed && toggle) {
                console.log('sidebar aperta al ridimensionamento della pagina');
                // If the sidebar is closed and the user has manually opened it, reopen it and save the state
                openSidebar();
            }
        }*/
    });

    // ---------------------------------------------END MANAGING SIDEBAR--------------------------------------------- // 
    if(localStorage.getItem('accessibility') == 'true'){
        console.log("ao")
        const checkbox=document.getElementById("checkbox");
        checkbox.setAttribute("checked","");
    }
});


function accessibility() {
    if(localStorage.getItem('accessibility')==null){
        localStorage.setItem('accessibility', true);
        // $.ajax({
        //     type: 'POST',
        //     url: '/accessibility',
        //     data: JSON.stringify({acc:true}),
        //     contentType: 'application/json',
        //     success: function(data) {
                
        //     }
        // });
    
    }
    if(localStorage.getItem('accessibility') == 'false'){
        localStorage.setItem('accessibility', true);
        // $.ajax({
        //     type: 'POST',
        //     url: '/accessibility',
        //     data: JSON.stringify({acc:true}),
        //     contentType: 'application/json',
        //     success: function(data) {
                
        //     }
        // });
        
    }
    else{
        localStorage.setItem('accessibility', false);
        // $.ajax({
        //     type: 'POST',
        //     url: '/accessibility',
        //     data: JSON.stringify({acc:false}),
        //     contentType: 'application/json',
        //     success: function(data) {
                
        //     }
        // });
        
    }   
    console.log(localStorage.getItem('accessibility')); 
    /*funzione toggle per i numeri*/
    toggleAcc();
}
var colori_home = ["white", "red", "darkgreen", "darkblue", "deeppink", "yellow","purple","aqua","sienna"];
function toggleAcc(){
    for (let i = 1; i < 9; i++) {
        for (let j = 1; j < 5; j++) {
            var targetDiv;
            targetDiv = document.getElementById(`text-ball-${i}-${j}`);
            if (targetDiv.innerHTML==''){
                colore_ball= document.getElementById(`ball-${i}-${j}`).style.backgroundColor;
                if(colore_ball != '' && colore_ball != 'white'){
                    targetDiv.innerHTML=colori_home.indexOf(colore_ball);
                }else{
                    targetDiv.innerHTML='';
                }
                
            }
            else{
                targetDiv.innerHTML='';
            }
        }
    }
}

var home_code=[];
var acc_home=localStorage.getItem('accessibility')
function fillhomeboard(){
   
    var numerorighe = Math.floor(Math.random() * 6) + 3;
    // Use the randomNumber variable as needed
    for (let i = 0; i < 4; i++) {
        home_code.push(Math.floor(Math.random() * 8)+1);
    }
    console.log(home_code);
    var bord_code =[];
    for (let i = 1; i < numerorighe+1; i++) {
        for (let j=0;j<4;j++){
            bord_code.push(Math.floor(Math.random() * 8)+1);
        }
        
        for (let j=1 ; j<5;j++){
            var targetDiv;
            targetDiv = document.getElementById(`ball-${i}-${j}`);
            targetDiv.style.backgroundColor = colori_home[bord_code[j-1]];
            if (acc_home=='true'){
                document.getElementById(`text-ball-${i}-${j}`).innerHTML=j-1;
            }
        }
        corretti=coonf_cod(bord_code,home_code,i)
        if(corretti==4){
            break;
        }
        bord_code=[];
    }
    
    
}

/*accessibilita nella board della home*/

/*gestione colori nella board della home*/
function coonf_cod(player_code, secret_code,x) {
    
    const copysc = [...secret_code];
    let posizioneCorretta = 0;
    let posizioneErrata = 0;
    let sbagliato = 0;
    let postrov = Array(player_code.length).fill(0);

    for (let i = 0; i < player_code.length; i++) {
        if (player_code[i] === copysc[i]) {
            postrov[i] = 1;
            posizioneCorretta++;
            copysc[i] = null;
        }
    }

    for (let i = 0; i < player_code.length; i++) {
        if (postrov[i] === 0) {
            if (copysc.includes(player_code[i])) {
                posizioneErrata++;
                const index = copysc.indexOf(player_code[i]);
                copysc[index] = null;
            } else {
                sbagliato++;
            }
        }
    }
    sug(posizioneCorretta,posizioneErrata,x)
    // Do something with the results (posizioneCorretta, posizioneErrata, sbagliato)
    return posizioneCorretta
}

function sug(correct,color,x){
    var occupato = [0,0,0,0];
    for (let i = 0; i < correct; i++) {
        var r = Math.floor(Math.random() * 4);
        if (occupato[r] === 0) {
            occupato[r] = 2;
            var sug = document.getElementById(`suggestion-${x}-${r+1}`);
            sug.classList.add("popup");
            sug.setAttribute("text", "Colore in posizione corretta");
            sug.innerHTML = '<div class="trangolo"></div>';
            sug.style.backgroundColor = "#7687AF";
            sug.style.border = "0"
            //mettimao un altro div dento per disegnare il triengolo e permettere di far apparire il popup
            var triang = suggestion.querySelector('.trangolo');
            triang.style.backgroundColor = "black";
            triang.style.clipPath = "polygon(50% 0%, 100% 100%, 0% 100%)";
            triang.style.borderBottom = "none";
        } else {
            i--;
        }
    }
    for (let i = 0; i < color; i++) {
        var r = Math.floor(Math.random() * 4);
        if (occupato[r] === 0) {
            occupato[r] = 1;
            var sug = document.getElementById(`suggestion-${x}-${r+1}`);
            sug.style.backgroundColor = "black";
            sug.style.borderRadius = "50%";
            sug.style.border = "1px solid black";
        } else {
            i--;
        }
    }
}



