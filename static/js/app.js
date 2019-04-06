Date.prototype.asMySQL = function() {
    let res = "" + this.getFullYear() + "-";
    res += ( this.getMonth() < 9 ? "0" : "" ) + ( this.getMonth() + 1 ) + "-";
    res += ( this.getDate() < 10 ? "0" : "" ) + this.getDate();
    return res;
}
Date.prototype.asMx = function() {
    let res = "";
    res += ( this.getDate() < 10 ? "0" : "" ) + this.getDate() + "/";
    res += ( this.getMonth() < 9 ? "0" : "" ) + ( this.getMonth() + 1 ) + "/" + this.getFullYear();
    return res;
}
Date.prototype.theTime = function() {
    let res = "";
    if ( this.getHours() < 10 ) {
        res += "0";
    }
    res += this.getHours() + ":";
    if ( this.getMinutes() < 10 ) {
        res += "0";
    }
    res += this.getMinutes();
    return res;
}
Number.prototype.asMoney = function() {
    let asString = `${this}`;
    if( asString.indexOf( "." ) == -1 ){
        asString += ".";
    }
    asString += "00";
    return asString.substr( 0, asString.indexOf( "." ) + 3 );
}

class clsApp {
    checkInputIn( idcontainer ) {
        $( '#' + idcontainer + ' input[type="checkbox"]' ).attr( 'checked', true );
    }
    uncheckInputIn( idcontainer ) {
        $( '#' + idcontainer + ' input[type="checkbox"]' ).attr( 'checked', false );
    }
    openPanel( body, title, close = true, footer = null ) {
        let template = Handlebars.compile( $( "#modal-panel-message-template" ).html() );
        let html = template( { title, body, footer, close } );
        $( "#modal-panel-message" ).remove();
        $( document.body ).append( $( html ) );
        $( "#modal-panel-message" ).modal();
    }
    setUIControls() {
        if( req_ui ) {
            $.datepicker.setDefaults( $.datepicker.regional[ "es" ] );
            $( `input[type="date"]` ).datepicker( {
                changeMonth: true,
                changeYear: true,
                dateFormat : 'yy-mm-dd'  
            } );
        }
    }
    setReadOnlyForm( container_selector = "#main-form" ) {
        let frm = $( container_selector );
        frm.find( "input" ).attr( "disabled", true );
        frm.find( "textarea" ).attr( "disabled", true );
        frm.find( "button" ).attr( "disabled", true );
        frm.find( "select" ).attr( "disabled", true );
        frm.find( "input" ).attr( "readonly", true );
        frm.find( "textarea" ).attr( "readonly", true );
        frm.find( "button" ).attr( "readonly", true );
        frm.find( "select" ).attr( "readonly", true );
        frm.find('input[type="file"]').parent().parent().remove();
        frm.find('input[type="number"]').each( function() {
            let valor = this.value;
            if( valor.indexOf( '.' ) >-1 ) {
                this.value = valor.substr( 0, valor.indexOf( '.' ) + 3 );
            }
        } );
        frm.find( "#btn-save" ).remove();
    }
    showPrivacyPolicy(){
        App.openPanel( $( "#privacy-policy-template" ).html(), "Política de Privacidad" );
    }
}

class clsCliente {
    showNotasSglCte() {
        App.openPanel( $( "#notas-template" ).html(), "Notas del Cliente" );
        App.setUIControls();
    }
    showAlertsSglCte() {
        App.openPanel( $( "#alerta-template" ).html(), "Alertas del Cliente" );
        App.setUIControls();
    }
}

let Cte = new clsCliente();
let App = new clsApp();

$( document ).ready( () => { 
    $('[data-toggle="tooltip"]').tooltip(); 
    App.setUIControls();
} );

