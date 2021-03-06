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
Date.prototype.fromMX = function( date ) {
    return new Date(
        parseInt( date.substr( 6, 4 ) ),
        parseInt( date.substr( 3, 4 ) ) - 1,
        parseInt( date.substr( 0, 2 ) )
        );
}
Date.prototype.addDays = function( days ) {
    let date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
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
    closePanel() {
        $("#modal-panel-message").remove();
        $('.modal-backdrop').remove();
        $(document.body).removeClass("modal-open");
        $(document.body).css("padding-right", "0px")
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
    showDeletingConfirmation(url, elemento="elemento", pre_elemento="el") {
        let template = Handlebars.compile( $( "#deleting-confirmation-template" ).html() );
        let html = template( { url, elemento, pre_elemento } );
        App.openPanel( html, "Confirmación de Eliminación");
        return false;
    }
    isEmpty( valor ) {
        return "" == valor || 0.0 == parseFloat( valor );
    }
    validate_required_fields( container ) {
        let elements = $(`${container} [required="required"]`);
        for( let idx = 0; idx <= elements.length; idx++){
            let element = $(elements[idx]);
            if(element.val() == "") {
                let lbl = element.parent().find('label');
                let msg = "El elemento ";
                if(lbl.length > 0) {
                    msg += lbl.text() + " ";
                }
                msg += "no puede estar vacío";
                alert(msg);
                element.focus();
                return false;
            }
        }
        return true;
    }
    sortDataGridReport(column_number, datatype) {
        var table, rows, switching, i, x, y, x_data, y_data, shouldSwitch, dir, switchcount = 0;
        $("#data-grid-report thead th .sort-sign-asc").addClass('d-none');
        $("#data-grid-report thead th .sort-sign-desc").addClass('d-none');
        table = $("#data-grid-report tbody");
        switching = true;
        dir = "asc";
        while (switching) {
            switching = false;
            rows = table.find('tr');
            for(i = 0; i < (rows.length - 1); i++) {
                shouldSwitch = false;
                x = $($(rows[i]).find("td")[column_number]);
                y = $($(rows[i + 1]).find("td")[column_number]);
                x_data = ("number" === datatype ?
                    Number(x.data('rawsortvalue'))
                    : x.data('rawsortvalue'));
                y_data = ("number" === datatype ?
                    Number(y.data('rawsortvalue'))
                    : y.data('rawsortvalue'));
                if("asc" == dir) {
                    if(x_data > y_data) {
                        shouldSwitch = true;
                        break;
                    }
                } else if("desc" == dir) {
                    if(x_data < y_data) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
            if(shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount++;
            } else {
                if (switchcount == 0 && dir == "asc") {
                    dir = "desc";
                    switching = true;
                }
            }
        }
        if("asc" == dir) {
            $($("#data-grid-report thead th .sort-sign-asc")[column_number]).removeClass('d-none');
        } else if("desc" == dir) {
            $($("#data-grid-report thead th .sort-sign-desc")[column_number]).removeClass('d-none');
        }
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
    showFrmDoctoGral() {
        App.openPanel( $( "#frmdoctogral-template").html(), "Adjuntar Documento" );
        App.setUIControls();
    }
}

class clsActividadHistoria {
    showFrmNew() {
        App.openPanel( $( "#frmactividadhistoria-template").html(), "Cambiar Estado de la Actividad" );
        App.setUIControls();
    }
}

let Cte = new clsCliente();
let App = new clsApp();
let ActividadHistoria = new clsActividadHistoria();

$( document ).ready( () => {
    $('[data-toggle="tooltip"]').tooltip();
    App.setUIControls();
} );

